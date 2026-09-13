import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from automation.exceptions import InvalidStateTransition


class TransitionModel(models.Model):
    TRANSITIONS = {}

    class Meta:
        abstract = True

    def transition_to(self, state):
        allowed = self.TRANSITIONS.get(self.status, set())
        if state not in allowed:
            raise InvalidStateTransition(f'{self.status} cannot transition to {state}.')
        self.status = state


class ActionApproval(TransitionModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        REVOKED = 'revoked', 'Revoked'
        EXPIRED = 'expired', 'Expired'
        CONSUMED = 'consumed', 'Consumed'

    TRANSITIONS = {
        Status.PENDING: {Status.APPROVED, Status.REJECTED, Status.REVOKED, Status.EXPIRED},
        Status.APPROVED: {Status.CONSUMED, Status.REVOKED, Status.EXPIRED},
    }

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.PROTECT, related_name='action_approvals')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='requested_action_approvals')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='reviewed_action_approvals')
    tool_name = models.CharField(max_length=120)
    tool_version = models.CharField(max_length=32)
    payload_fingerprint = models.CharField(max_length=64)
    policy_fingerprint = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    reviewed_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=('workspace', 'status', 'expires_at'), name='approval_ws_state_idx'),
            models.Index(fields=('payload_fingerprint', 'policy_fingerprint'), name='approval_fprints_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=['pending', 'approved', 'rejected', 'revoked', 'expired', 'consumed']),
                name='approval_valid_status',
            ),
        ]
        permissions = [('decide_actionapproval', 'Can approve or reject automation actions')]


class AutomationCommand(TransitionModel):
    class Effect(models.TextChoices):
        READ = 'read', 'Read only'
        DRAFT = 'draft', 'Draft-producing'
        MUTATE_INTERNAL = 'mutate_internal', 'Internal mutation'
        CONSEQUENTIAL = 'consequential', 'External or consequential effect'

    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    TRANSITIONS = {
        Status.QUEUED: {Status.RUNNING, Status.CANCELLED, Status.FAILED},
        Status.RUNNING: {Status.SUCCEEDED, Status.FAILED, Status.CANCELLED},
    }

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.PROTECT, related_name='automation_commands')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='automation_commands')
    approval = models.OneToOneField(ActionApproval, null=True, blank=True, on_delete=models.PROTECT, related_name='command')
    tool_name = models.CharField(max_length=120)
    tool_version = models.CharField(max_length=32)
    effect = models.CharField(max_length=20, choices=Effect.choices)
    payload = models.JSONField(default=dict)
    payload_fingerprint = models.CharField(max_length=64)
    policy_fingerprint = models.CharField(max_length=64)
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    result = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=('workspace', 'status', '-created_at'), name='command_ws_state_idx'),
            models.Index(fields=('tool_name', 'tool_version', '-created_at'), name='command_tool_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=('workspace', 'idempotency_key'), name='command_ws_idem_uniq'),
            models.CheckConstraint(
                condition=Q(status__in=['queued', 'running', 'succeeded', 'failed', 'cancelled']),
                name='command_valid_status',
            ),
            models.CheckConstraint(
                condition=Q(effect__in=['read', 'draft', 'mutate_internal', 'consequential']),
                name='command_valid_effect',
            ),
            models.CheckConstraint(
                condition=~Q(effect='consequential') | Q(approval__isnull=False),
                name='consequential_has_approval',
            ),
        ]


class OutboxEvent(TransitionModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        DISPATCHING = 'dispatching', 'Dispatching'
        PUBLISHED = 'published', 'Published'
        FAILED = 'failed', 'Failed'
        DEAD = 'dead', 'Dead lettered'

    TRANSITIONS = {
        Status.PENDING: {Status.DISPATCHING, Status.DEAD},
        Status.DISPATCHING: {Status.PUBLISHED, Status.FAILED, Status.DEAD},
        Status.FAILED: {Status.PENDING, Status.DEAD},
    }

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.PROTECT, related_name='outbox_events')
    command = models.ForeignKey(AutomationCommand, on_delete=models.PROTECT, related_name='outbox_events')
    event_type = models.CharField(max_length=120, default='automation.command.requested')
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    available_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=('status', 'available_at'), name='outbox_ready_idx')]
        constraints = [
            models.UniqueConstraint(fields=('command', 'event_type'), name='outbox_command_event_uniq'),
            models.CheckConstraint(
                condition=Q(status__in=['pending', 'dispatching', 'published', 'failed', 'dead']),
                name='outbox_valid_status',
            ),
        ]


class WorkflowExecution(TransitionModel):
    class Status(models.TextChoices):
        CREATED = 'created', 'Created'
        RUNNING = 'running', 'Running'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    TRANSITIONS = {
        Status.CREATED: {Status.RUNNING, Status.FAILED, Status.CANCELLED},
        Status.RUNNING: {Status.SUCCEEDED, Status.FAILED, Status.CANCELLED},
    }

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.PROTECT, related_name='workflow_executions')
    command = models.ForeignKey(AutomationCommand, on_delete=models.PROTECT, related_name='executions')
    workflow_name = models.CharField(max_length=120)
    workflow_version = models.CharField(max_length=32)
    grant_jti = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider_execution_id = models.CharField(max_length=160, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CREATED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=('workspace', 'status', '-created_at'), name='execution_ws_state_idx')]
        constraints = [
            models.UniqueConstraint(fields=('workflow_name', 'provider_execution_id'), condition=Q(provider_execution_id__isnull=False), name='execution_provider_uniq'),
            models.CheckConstraint(
                condition=Q(status__in=['created', 'running', 'succeeded', 'failed', 'cancelled']),
                name='execution_valid_status',
            ),
        ]


class CallbackReceipt(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    execution = models.ForeignKey(WorkflowExecution, on_delete=models.PROTECT, related_name='callback_receipts')
    idempotency_key = models.CharField(max_length=128)
    nonce = models.UUIDField(unique=True)
    payload_hash = models.CharField(max_length=64)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('execution', 'idempotency_key'), name='callback_execution_idem_uniq'),
        ]


class DeadLetter(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.PROTECT, related_name='dead_letters')
    outbox_event = models.OneToOneField(OutboxEvent, on_delete=models.PROTECT, related_name='dead_letter')
    command = models.ForeignKey(AutomationCommand, on_delete=models.PROTECT, related_name='dead_letters')
    reason_code = models.CharField(max_length=80)
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=('workspace', 'resolved_at', '-created_at'), name='deadletter_open_idx')]
