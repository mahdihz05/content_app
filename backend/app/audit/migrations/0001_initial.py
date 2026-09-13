from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


def install_append_only_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(
        """
        CREATE OR REPLACE FUNCTION audit_event_append_only() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_auditevent is append-only';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER audit_event_no_update_delete
        BEFORE UPDATE OR DELETE ON audit_auditevent
        FOR EACH ROW EXECUTE FUNCTION audit_event_append_only();
        """
    )


def remove_append_only_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(
        """
        DROP TRIGGER IF EXISTS audit_event_no_update_delete ON audit_auditevent;
        DROP FUNCTION IF EXISTS audit_event_append_only();
        """
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('event_type', models.CharField(max_length=120)),
                ('target_type', models.CharField(max_length=120)),
                ('target_public_id', models.UUIDField(blank=True, null=True)),
                ('correlation_id', models.CharField(blank=True, max_length=128)),
                ('payload', models.JSONField(default=dict)),
                ('occurred_at', models.DateTimeField(auto_now_add=True, editable=False)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='v2_audit_events', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='audit_events', to='workspaces.workspace')),
            ],
            options={'ordering': ('occurred_at', 'id')},
        ),
        migrations.AddIndex(model_name='auditevent', index=models.Index(fields=['workspace', '-occurred_at'], name='audit_ws_time_idx')),
        migrations.AddIndex(model_name='auditevent', index=models.Index(fields=['event_type', '-occurred_at'], name='audit_type_time_idx')),
        migrations.AddIndex(model_name='auditevent', index=models.Index(fields=['target_type', 'target_public_id'], name='audit_target_idx')),
        migrations.RunPython(install_append_only_trigger, remove_append_only_trigger),
    ]
