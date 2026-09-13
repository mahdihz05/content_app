from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workspaces', '0001_initial'),
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('tool_name', models.CharField(max_length=120)),
                ('tool_version', models.CharField(max_length=32)),
                ('payload_fingerprint', models.CharField(max_length=64)),
                ('policy_fingerprint', models.CharField(max_length=64)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('revoked', 'Revoked'), ('expired', 'Expired'), ('consumed', 'Consumed')], default='pending', max_length=16)),
                ('reason', models.TextField(blank=True)),
                ('expires_at', models.DateTimeField()),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('consumed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requested_action_approvals', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviewed_action_approvals', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='action_approvals', to='workspaces.workspace')),
            ],
            options={
                'permissions': [('decide_actionapproval', 'Can approve or reject automation actions')],
                'indexes': [models.Index(fields=['workspace', 'status', 'expires_at'], name='approval_ws_state_idx'), models.Index(fields=['payload_fingerprint', 'policy_fingerprint'], name='approval_fprints_idx')],
                'constraints': [models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'approved', 'rejected', 'revoked', 'expired', 'consumed'])), name='approval_valid_status')],
            },
        ),
        migrations.CreateModel(
            name='AutomationCommand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('tool_name', models.CharField(max_length=120)),
                ('tool_version', models.CharField(max_length=32)),
                ('effect', models.CharField(choices=[('read', 'Read only'), ('draft', 'Draft-producing'), ('mutate_internal', 'Internal mutation'), ('consequential', 'External or consequential effect')], max_length=20)),
                ('payload', models.JSONField(default=dict)),
                ('payload_fingerprint', models.CharField(max_length=64)),
                ('policy_fingerprint', models.CharField(max_length=64)),
                ('idempotency_key', models.CharField(max_length=128)),
                ('status', models.CharField(choices=[('queued', 'Queued'), ('running', 'Running'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='queued', max_length=16)),
                ('result', models.JSONField(blank=True, default=dict)),
                ('error_code', models.CharField(blank=True, max_length=80)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='automation_commands', to=settings.AUTH_USER_MODEL)),
                ('approval', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='command', to='automation.actionapproval')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='automation_commands', to='workspaces.workspace')),
            ],
            options={
                'indexes': [models.Index(fields=['workspace', 'status', '-created_at'], name='command_ws_state_idx'), models.Index(fields=['tool_name', 'tool_version', '-created_at'], name='command_tool_idx')],
                'constraints': [
                    models.UniqueConstraint(fields=('workspace', 'idempotency_key'), name='command_ws_idem_uniq'),
                    models.CheckConstraint(condition=models.Q(('status__in', ['queued', 'running', 'succeeded', 'failed', 'cancelled'])), name='command_valid_status'),
                    models.CheckConstraint(condition=models.Q(('effect__in', ['read', 'draft', 'mutate_internal', 'consequential'])), name='command_valid_effect'),
                    models.CheckConstraint(condition=models.Q(('effect', 'consequential'), _negated=True) | models.Q(('approval__isnull', False)), name='consequential_has_approval'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OutboxEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('event_type', models.CharField(default='automation.command.requested', max_length=120)),
                ('payload', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('dispatching', 'Dispatching'), ('published', 'Published'), ('failed', 'Failed'), ('dead', 'Dead lettered')], default='pending', max_length=16)),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('available_at', models.DateTimeField()),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='outbox_events', to='automation.automationcommand')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='outbox_events', to='workspaces.workspace')),
            ],
            options={
                'indexes': [models.Index(fields=['status', 'available_at'], name='outbox_ready_idx')],
                'constraints': [models.UniqueConstraint(fields=('command', 'event_type'), name='outbox_command_event_uniq'), models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'dispatching', 'published', 'failed', 'dead'])), name='outbox_valid_status')],
            },
        ),
        migrations.CreateModel(
            name='WorkflowExecution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('workflow_name', models.CharField(max_length=120)),
                ('workflow_version', models.CharField(max_length=32)),
                ('grant_jti', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('provider_execution_id', models.CharField(blank=True, max_length=160, null=True)),
                ('status', models.CharField(choices=[('created', 'Created'), ('running', 'Running'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='created', max_length=16)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='executions', to='automation.automationcommand')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='workflow_executions', to='workspaces.workspace')),
            ],
            options={
                'indexes': [models.Index(fields=['workspace', 'status', '-created_at'], name='execution_ws_state_idx')],
                'constraints': [models.UniqueConstraint(condition=models.Q(('provider_execution_id__isnull', False)), fields=('workflow_name', 'provider_execution_id'), name='execution_provider_uniq'), models.CheckConstraint(condition=models.Q(('status__in', ['created', 'running', 'succeeded', 'failed', 'cancelled'])), name='execution_valid_status')],
            },
        ),
        migrations.CreateModel(
            name='CallbackReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('idempotency_key', models.CharField(max_length=128)),
                ('nonce', models.UUIDField(unique=True)),
                ('payload_hash', models.CharField(max_length=64)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='callback_receipts', to='automation.workflowexecution')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('execution', 'idempotency_key'), name='callback_execution_idem_uniq')]},
        ),
        migrations.CreateModel(
            name='DeadLetter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('reason_code', models.CharField(max_length=80)),
                ('detail', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dead_letters', to='automation.automationcommand')),
                ('outbox_event', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='dead_letter', to='automation.outboxevent')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dead_letters', to='workspaces.workspace')),
            ],
            options={'indexes': [models.Index(fields=['workspace', 'resolved_at', '-created_at'], name='deadletter_open_idx')]},
        ),
    ]
