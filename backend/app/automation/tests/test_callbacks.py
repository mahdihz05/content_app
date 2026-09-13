import time
import uuid

from django.test import TestCase

from audit.models import AuditEvent
from automation.callbacks import accept_callback
from automation.exceptions import CallbackReplay, InvalidCallback, InvalidGrant
from automation.models import AutomationCommand, CallbackReceipt, WorkflowExecution
from automation.registry import PolicyDecision, ToolRegistry, ToolSpec
from automation.services import create_command
from automation.signing import callback_signature, issue_execution_grant, verify_execution_grant
from automation.tests.factories import create_workspace
from user.models import CustomUser


class SignedCallbackTests(TestCase):
    def setUp(self):
        self.actor = CustomUser.objects.create_user('09120000061', 'password')
        self.workspace = create_workspace(self.actor, 'callbacks')
        self.registry = ToolRegistry()
        self.registry.register(ToolSpec(
            'connection.verify', '1', 'mutate_internal', 'connection.verify', '1',
            {'type': 'object', 'required': ['connection_id'], 'properties': {'connection_id': {'type': 'string'}}},
            {'type': 'object', 'required': ['verified'], 'properties': {'verified': {'type': 'boolean'}}},
        ))
        payload = {'connection_id': 'connection-1'}
        preflight = self.registry.preflight(
            name='connection.verify', version='1', payload=payload,
            actor=self.actor, workspace=self.workspace,
            policy_evaluator=lambda **kwargs: PolicyDecision(True, False, 'policy-1'),
        )
        self.command, _ = create_command(
            workspace=self.workspace, actor=self.actor, idempotency_key='verify-1',
            preflight=preflight, payload=payload,
        )
        self.execution = WorkflowExecution.objects.create(
            workspace=self.workspace,
            command=self.command,
            workflow_name='connection.verify',
            workflow_version='1',
        )
        self.grant = issue_execution_grant(
            execution=self.execution,
            scopes=['execution:callback'],
        )
        self.claims = verify_execution_grant(self.grant, required_scope='execution:callback')

    def callback(self, body, key='callback-1', nonce=None, signature=None):
        timestamp = int(time.time())
        nonce = nonce or uuid.uuid4()
        signature = signature or callback_signature(
            callback_secret=self.claims['callback_secret'],
            timestamp=timestamp,
            nonce=nonce,
            idempotency_key=key,
            body=body,
        )
        return accept_callback(
            grant=self.grant,
            timestamp=timestamp,
            nonce=nonce,
            idempotency_key=key,
            signature=signature,
            body=body,
            tool_registry=self.registry,
        )

    def test_signed_result_transitions_execution_and_command(self):
        execution, duplicate = self.callback({
            'contract_version': 'v1',
            'status': 'succeeded',
            'result': {'verified': True},
        })
        self.assertFalse(duplicate)
        self.assertEqual(execution.status, WorkflowExecution.Status.SUCCEEDED)
        self.command.refresh_from_db()
        self.assertEqual(self.command.status, AutomationCommand.Status.SUCCEEDED)
        self.assertEqual(CallbackReceipt.objects.count(), 1)
        self.assertTrue(AuditEvent.objects.filter(event_type='automation.callback.succeeded').exists())

    def test_identical_idempotency_key_and_payload_is_a_noop(self):
        body = {'contract_version': 'v1', 'status': 'succeeded', 'result': {'verified': True}}
        self.callback(body)
        _, duplicate = self.callback(body, nonce=uuid.uuid4())
        self.assertTrue(duplicate)
        self.assertEqual(CallbackReceipt.objects.count(), 1)

    def test_changed_payload_for_idempotency_key_is_replay(self):
        self.callback({'contract_version': 'v1', 'status': 'succeeded', 'result': {'verified': True}})
        with self.assertRaises(CallbackReplay):
            self.callback({'contract_version': 'v1', 'status': 'succeeded', 'result': {'verified': False}})

    def test_nonce_cannot_be_reused_for_another_callback(self):
        nonce = uuid.uuid4()
        self.callback({'contract_version': 'v1', 'status': 'running'}, nonce=nonce)
        with self.assertRaises(CallbackReplay):
            self.callback(
                {'contract_version': 'v1', 'status': 'succeeded', 'result': {'verified': True}},
                key='callback-2', nonce=nonce,
            )

    def test_forged_signature_and_invalid_result_are_rejected(self):
        with self.assertRaises(InvalidCallback):
            self.callback({'contract_version': 'v1', 'status': 'running'}, signature='0' * 64)
        with self.assertRaises(InvalidCallback):
            self.callback({'contract_version': 'v1', 'status': 'succeeded', 'result': {'verified': 'yes'}})
        self.assertEqual(CallbackReceipt.objects.count(), 0)

    def test_expired_and_wrong_scope_grants_are_rejected(self):
        expired = issue_execution_grant(
            execution=self.execution,
            scopes=['execution:callback'],
            ttl_seconds=1,
            now=int(time.time()) - 2,
        )
        with self.assertRaises(InvalidGrant):
            verify_execution_grant(expired, required_scope='execution:callback')
        wrong_scope = issue_execution_grant(execution=self.execution, scopes=['execution:read'])
        with self.assertRaises(InvalidGrant):
            verify_execution_grant(wrong_scope, required_scope='execution:callback')
