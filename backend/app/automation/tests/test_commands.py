from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from audit.models import AuditEvent
from automation.exceptions import ApprovalInvalid, IdempotencyConflict
from automation.models import ActionApproval, AutomationCommand, OutboxEvent
from automation.registry import PolicyDecision, ToolRegistry, ToolSpec
from automation.services import create_command, decide_approval, request_approval
from automation.tests.factories import create_workspace
from user.models import CustomUser


class CommandTransactionTests(TestCase):
    def setUp(self):
        self.actor = CustomUser.objects.create_user('09120000051', 'password')
        self.reviewer = CustomUser.objects.create_user('09120000052', 'password')
        self.workspace = create_workspace(self.actor)
        self.registry = ToolRegistry()
        self.registry.register(ToolSpec(
            'content.publish', '1', 'consequential', 'content.publish', '1',
            {'type': 'object', 'required': ['content_id'], 'additionalProperties': False, 'properties': {'content_id': {'type': 'string'}}},
            {'type': 'object'},
        ))

    def preflight(self, payload, policy_version='1'):
        return self.registry.preflight(
            name='content.publish', version='1', payload=payload,
            actor=self.actor, workspace=self.workspace,
            policy_evaluator=lambda **kwargs: PolicyDecision(True, True, policy_version),
        )

    def approved(self, preflight, expires_at=None):
        approval = request_approval(
            workspace=self.workspace,
            actor=self.actor,
            preflight=preflight,
            expires_at=expires_at or timezone.now() + timedelta(minutes=5),
        )
        return decide_approval(approval=approval, reviewer=self.reviewer, approve=True)

    def test_command_outbox_audit_and_approval_are_atomic_and_idempotent(self):
        payload = {'content_id': 'content-1'}
        preflight = self.preflight(payload)
        approval = self.approved(preflight)
        command, created = create_command(
            workspace=self.workspace, actor=self.actor, idempotency_key='publish-1',
            preflight=preflight, payload=payload, approval=approval,
        )
        repeated, repeated_created = create_command(
            workspace=self.workspace, actor=self.actor, idempotency_key='publish-1',
            preflight=preflight, payload=payload, approval=approval,
        )
        self.assertTrue(created)
        self.assertFalse(repeated_created)
        self.assertEqual(command.pk, repeated.pk)
        self.assertEqual(OutboxEvent.objects.filter(command=command).count(), 1)
        self.assertEqual(AuditEvent.objects.filter(target_public_id=command.public_id).count(), 1)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ActionApproval.Status.CONSUMED)

    def test_same_idempotency_key_with_changed_payload_conflicts(self):
        first_payload = {'content_id': 'one'}
        first = self.preflight(first_payload)
        create_command(workspace=self.workspace, actor=self.actor, idempotency_key='same', preflight=first, payload=first_payload, approval=self.approved(first))
        second_payload = {'content_id': 'two'}
        second = self.preflight(second_payload)
        with self.assertRaises(IdempotencyConflict):
            create_command(workspace=self.workspace, actor=self.actor, idempotency_key='same', preflight=second, payload=second_payload, approval=self.approved(second))

    def test_policy_or_payload_change_invalidates_approval(self):
        approval = self.approved(self.preflight({'content_id': 'one'}))
        changed = self.preflight({'content_id': 'two'}, policy_version='2')
        with self.assertRaises(ApprovalInvalid):
            create_command(workspace=self.workspace, actor=self.actor, idempotency_key='changed', preflight=changed, payload={'content_id': 'two'}, approval=approval)

    def test_approval_is_bound_once(self):
        payload = {'content_id': 'one'}
        preflight = self.preflight(payload)
        approval = self.approved(preflight)
        create_command(workspace=self.workspace, actor=self.actor, idempotency_key='first', preflight=preflight, payload=payload, approval=approval)
        approval.refresh_from_db()
        with self.assertRaises(ApprovalInvalid):
            create_command(workspace=self.workspace, actor=self.actor, idempotency_key='second', preflight=preflight, payload=payload, approval=approval)

    def test_approval_is_bound_to_requesting_actor(self):
        payload = {'content_id': 'one'}
        preflight = self.preflight(payload)
        approval = self.approved(preflight)
        other_preflight = self.registry.preflight(
            name='content.publish', version='1', payload=payload,
            actor=self.reviewer, workspace=self.workspace,
            policy_evaluator=lambda **kwargs: PolicyDecision(True, True, '1'),
        )
        with self.assertRaises(ApprovalInvalid):
            create_command(
                workspace=self.workspace, actor=self.reviewer, idempotency_key='other-actor',
                preflight=other_preflight, payload=payload, approval=approval,
            )

    def test_expired_approval_is_rejected(self):
        preflight = self.preflight({'content_id': 'one'})
        approval = self.approved(preflight)
        ActionApproval.objects.filter(pk=approval.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        approval.refresh_from_db()
        with self.assertRaises(ApprovalInvalid):
            create_command(workspace=self.workspace, actor=self.actor, idempotency_key='expired', preflight=preflight, payload={'content_id': 'one'}, approval=approval)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ActionApproval.Status.EXPIRED)

    def test_audit_failure_rolls_back_command_and_outbox(self):
        payload = {'content_id': 'one'}
        preflight = self.preflight(payload)
        approval = self.approved(preflight)
        before = AuditEvent.objects.count()
        with patch('automation.services.AuditEvent.objects.append', side_effect=RuntimeError('audit unavailable')):
            with self.assertRaises(RuntimeError):
                create_command(workspace=self.workspace, actor=self.actor, idempotency_key='rollback', preflight=preflight, payload=payload, approval=approval)
        self.assertFalse(AutomationCommand.objects.filter(idempotency_key='rollback').exists())
        self.assertFalse(OutboxEvent.objects.filter(command__idempotency_key='rollback').exists())
        self.assertEqual(AuditEvent.objects.count(), before)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ActionApproval.Status.APPROVED)
