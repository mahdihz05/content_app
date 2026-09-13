from django.db import IntegrityError, transaction
from django.utils import timezone

from audit.models import AuditEvent
from automation.exceptions import (
    ApprovalInvalid,
    ApprovalRequired,
    ContractValidationError,
    IdempotencyConflict,
)
from automation.fingerprints import fingerprint
from automation.models import ActionApproval, AutomationCommand, OutboxEvent


def _same_command(command, *, actor, preflight):
    return (
        command.actor_id == actor.pk
        and command.tool_name == preflight.spec.name
        and command.tool_version == preflight.spec.version
        and command.effect == preflight.spec.effect
        and command.payload_fingerprint == preflight.payload_fingerprint
        and command.policy_fingerprint == preflight.policy_fingerprint
    )


@transaction.atomic
def request_approval(*, workspace, actor, preflight, expires_at, correlation_id=''):
    now = timezone.now()
    if expires_at <= now:
        raise ApprovalInvalid('Approval expiry must be in the future.')
    approval = ActionApproval.objects.create(
        workspace=workspace,
        requested_by=actor,
        tool_name=preflight.spec.name,
        tool_version=preflight.spec.version,
        payload_fingerprint=preflight.payload_fingerprint,
        policy_fingerprint=preflight.policy_fingerprint,
        expires_at=expires_at,
    )
    AuditEvent.objects.append(
        workspace=workspace,
        actor=actor,
        event_type='automation.approval.requested',
        target_type='automation.ActionApproval',
        target_public_id=approval.public_id,
        correlation_id=correlation_id,
        payload={
            'tool_name': approval.tool_name,
            'tool_version': approval.tool_version,
            'payload_fingerprint': approval.payload_fingerprint,
            'policy_fingerprint': approval.policy_fingerprint,
        },
    )
    return approval


def decide_approval(*, approval, reviewer, approve, reason='', correlation_id=''):
    expired = False
    with transaction.atomic():
        locked = ActionApproval.objects.select_for_update().get(pk=approval.pk)
        now = timezone.now()
        if locked.status != ActionApproval.Status.PENDING:
            raise ApprovalInvalid('Approval has already been decided.')
        if locked.expires_at <= now:
            locked.transition_to(ActionApproval.Status.EXPIRED)
            expired = True
        else:
            locked.transition_to(ActionApproval.Status.APPROVED if approve else ActionApproval.Status.REJECTED)
            locked.reviewed_by = reviewer
            locked.reviewed_at = now
            locked.reason = reason
        locked.save(update_fields=('status', 'reviewed_by', 'reviewed_at', 'reason', 'updated_at'))
        AuditEvent.objects.append(
            workspace=locked.workspace,
            actor=reviewer,
            event_type=f'automation.approval.{locked.status}',
            target_type='automation.ActionApproval',
            target_public_id=locked.public_id,
            correlation_id=correlation_id,
            payload={'reason': reason},
        )
    if expired:
        raise ApprovalInvalid('Approval has expired.')
    return locked


def expire_approval(*, approval, correlation_id=''):
    with transaction.atomic():
        locked = ActionApproval.objects.select_for_update().get(pk=approval.pk)
        if locked.expires_at > timezone.now():
            return False
        if locked.status not in {ActionApproval.Status.PENDING, ActionApproval.Status.APPROVED}:
            return locked.status == ActionApproval.Status.EXPIRED
        locked.transition_to(ActionApproval.Status.EXPIRED)
        locked.save(update_fields=('status', 'updated_at'))
        AuditEvent.objects.append(
            workspace=locked.workspace,
            actor=None,
            event_type='automation.approval.expired',
            target_type='automation.ActionApproval',
            target_public_id=locked.public_id,
            correlation_id=correlation_id,
        )
        return True


def create_command(
    *, workspace, actor, idempotency_key, preflight, payload, approval=None, correlation_id=''
):
    if not idempotency_key or len(idempotency_key) > 128:
        raise ContractValidationError(['Idempotency key must contain 1-128 characters.'])
    if fingerprint(payload) != preflight.payload_fingerprint:
        raise ContractValidationError(['Payload changed after policy preflight.'])
    existing = AutomationCommand.objects.filter(
        workspace=workspace,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        if not _same_command(existing, actor=actor, preflight=preflight):
            raise IdempotencyConflict('Idempotency key is bound to another command request.')
        return existing, False

    if (
        preflight.spec.effect == AutomationCommand.Effect.CONSEQUENTIAL
        and approval is not None
        and expire_approval(approval=approval, correlation_id=correlation_id)
    ):
        raise ApprovalInvalid('Approval has expired.')

    try:
        with transaction.atomic():
            locked_approval = None
            if preflight.spec.effect == AutomationCommand.Effect.CONSEQUENTIAL:
                if approval is None:
                    raise ApprovalRequired('A valid approval is required.')
                locked_approval = ActionApproval.objects.select_for_update().get(pk=approval.pk)
                now = timezone.now()
                if locked_approval.status != ActionApproval.Status.APPROVED:
                    concurrent = AutomationCommand.objects.filter(
                        workspace=workspace,
                        idempotency_key=idempotency_key,
                    ).first()
                    if concurrent and _same_command(concurrent, actor=actor, preflight=preflight):
                        return concurrent, False
                    raise ApprovalInvalid('Approval is not approved or was already consumed.')
                if locked_approval.expires_at <= now:
                    raise ApprovalInvalid('Approval has expired.')
                expected = (
                    locked_approval.workspace_id == workspace.pk
                    and locked_approval.requested_by_id == actor.pk
                    and locked_approval.tool_name == preflight.spec.name
                    and locked_approval.tool_version == preflight.spec.version
                    and locked_approval.payload_fingerprint == preflight.payload_fingerprint
                    and locked_approval.policy_fingerprint == preflight.policy_fingerprint
                )
                if not expected:
                    raise ApprovalInvalid('Approval does not match the exact command and policy.')

            command = AutomationCommand.objects.create(
                workspace=workspace,
                actor=actor,
                approval=locked_approval,
                tool_name=preflight.spec.name,
                tool_version=preflight.spec.version,
                effect=preflight.spec.effect,
                payload=payload,
                payload_fingerprint=preflight.payload_fingerprint,
                policy_fingerprint=preflight.policy_fingerprint,
                idempotency_key=idempotency_key,
            )
            OutboxEvent.objects.create(
                workspace=workspace,
                command=command,
                payload={
                    'contract_version': 'v1',
                    'command_id': str(command.public_id),
                    'workspace_id': str(workspace.public_id),
                    'tool_name': command.tool_name,
                    'tool_version': command.tool_version,
                    'workflow_name': preflight.spec.workflow_name,
                    'workflow_version': preflight.spec.workflow_version,
                },
                available_at=timezone.now(),
            )
            AuditEvent.objects.append(
                workspace=workspace,
                actor=actor,
                event_type='automation.command.created',
                target_type='automation.AutomationCommand',
                target_public_id=command.public_id,
                correlation_id=correlation_id,
                payload={
                    'effect': command.effect,
                    'tool_name': command.tool_name,
                    'tool_version': command.tool_version,
                    'payload_fingerprint': command.payload_fingerprint,
                    'policy_fingerprint': command.policy_fingerprint,
                },
            )
            if locked_approval:
                locked_approval.transition_to(ActionApproval.Status.CONSUMED)
                locked_approval.consumed_at = timezone.now()
                locked_approval.save(update_fields=('status', 'consumed_at', 'updated_at'))
            return command, True
    except IntegrityError:
        existing = AutomationCommand.objects.filter(
            workspace=workspace,
            idempotency_key=idempotency_key,
        ).first()
        if existing and _same_command(existing, actor=actor, preflight=preflight):
            return existing, False
        raise IdempotencyConflict('Idempotency key is bound to another command request.')
