import uuid

from django.db import IntegrityError, transaction
from django.utils import timezone

from audit.models import AuditEvent
from automation.exceptions import CallbackReplay, InvalidCallback, InvalidGrant
from automation.models import AutomationCommand, CallbackReceipt, WorkflowExecution
from automation.registry import registry, validate_schema
from automation.signing import verify_callback_signature, verify_execution_grant


CALLBACK_SCHEMA = {
    'type': 'object',
    'required': ['contract_version', 'status'],
    'additionalProperties': False,
    'properties': {
        'contract_version': {'type': 'string', 'enum': ['v1']},
        'status': {'type': 'string', 'enum': ['running', 'succeeded', 'failed']},
        'result': {'type': 'object'},
        'error': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'code': {'type': 'string', 'maxLength': 80},
                'message': {'type': 'string', 'maxLength': 500},
            },
        },
    },
}


def _verify_claim_binding(claims, execution):
    expected = {
        'jti': str(execution.grant_jti),
        'command_id': str(execution.command.public_id),
        'execution_id': str(execution.public_id),
        'workspace_id': str(execution.workspace.public_id),
        'workflow_name': execution.workflow_name,
        'workflow_version': execution.workflow_version,
    }
    if any(claims[name] != value for name, value in expected.items()):
        raise InvalidGrant('Execution grant scope does not match the execution.')


def accept_callback(
    *, grant, timestamp, nonce, idempotency_key, signature, body, correlation_id='',
    tool_registry=registry,
):
    claims = verify_execution_grant(grant, required_scope='execution:callback')
    errors = validate_schema(body, CALLBACK_SCHEMA)
    if errors:
        raise InvalidCallback('; '.join(errors))
    payload_hash = verify_callback_signature(
        claims=claims,
        timestamp=timestamp,
        nonce=nonce,
        idempotency_key=idempotency_key,
        body=body,
        signature=signature,
    )

    with transaction.atomic():
        try:
            execution = WorkflowExecution.objects.select_for_update().select_related(
                'command', 'workspace'
            ).get(public_id=claims['execution_id'])
        except WorkflowExecution.DoesNotExist as exc:
            raise InvalidGrant('Execution grant target does not exist.') from exc
        _verify_claim_binding(claims, execution)

        if body['status'] == WorkflowExecution.Status.SUCCEEDED:
            spec = tool_registry.get(execution.command.tool_name, execution.command.tool_version)
            result_errors = validate_schema(body.get('result'), spec.result_schema, '$.result')
            if result_errors:
                raise InvalidCallback('; '.join(result_errors))

        prior = CallbackReceipt.objects.filter(
            execution=execution,
            idempotency_key=idempotency_key,
        ).first()
        if prior:
            if prior.payload_hash != payload_hash:
                raise CallbackReplay('Callback idempotency key was reused with another payload.')
            return execution, True
        if CallbackReceipt.objects.filter(nonce=nonce).exists():
            raise CallbackReplay('Callback nonce has already been used.')

        command = AutomationCommand.objects.select_for_update().get(pk=execution.command_id)
        target = body['status']
        now = timezone.now()
        if target == WorkflowExecution.Status.RUNNING:
            execution.transition_to(target)
            execution.started_at = now
            execution.save(update_fields=('status', 'started_at', 'updated_at'))
            if command.status == AutomationCommand.Status.QUEUED:
                command.transition_to(AutomationCommand.Status.RUNNING)
                command.started_at = now
                command.save(update_fields=('status', 'started_at', 'updated_at'))
        else:
            if execution.status == WorkflowExecution.Status.CREATED:
                execution.transition_to(WorkflowExecution.Status.RUNNING)
                execution.started_at = now
            execution.transition_to(target)
            execution.completed_at = now
            execution.save(update_fields=('status', 'started_at', 'completed_at', 'updated_at'))
            if command.status == AutomationCommand.Status.QUEUED:
                command.transition_to(AutomationCommand.Status.RUNNING)
                command.started_at = now
            command.transition_to(target)
            command.completed_at = now
            command.result = body.get('result', {})
            command.error_code = body.get('error', {}).get('code', '')
            command.save(update_fields=(
                'status', 'started_at', 'completed_at', 'result', 'error_code', 'updated_at'
            ))

        try:
            receipt = CallbackReceipt.objects.create(
                execution=execution,
                nonce=uuid.UUID(str(nonce)),
                idempotency_key=idempotency_key,
                payload_hash=payload_hash,
            )
        except IntegrityError as exc:
            raise CallbackReplay('Callback identifiers have already been used.') from exc
        AuditEvent.objects.append(
            workspace=execution.workspace,
            actor=None,
            event_type=f'automation.callback.{target}',
            target_type='automation.WorkflowExecution',
            target_public_id=execution.public_id,
            correlation_id=correlation_id,
            payload={
                'callback_id': str(receipt.public_id),
                'command_id': str(command.public_id),
                'idempotency_key': idempotency_key,
                'payload_hash': payload_hash,
            },
        )
        return execution, False
