import uuid

from django.conf import settings
from django.db import models


REDACTED = '[REDACTED]'
SENSITIVE_KEYS = {
    'access_token',
    'api_key',
    'authorization',
    'cookie',
    'credential',
    'credentials',
    'password',
    'refresh_token',
    'secret',
    'session',
    'token',
}


def redact(value):
    """Return a JSON-safe copy with credential-shaped values removed."""
    if isinstance(value, dict):
        return {
            str(key): REDACTED if str(key).lower() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    return value


class AppendOnlyAuditQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise TypeError('Audit events are append-only.')

    def delete(self):
        raise TypeError('Audit events are append-only.')

    def bulk_update(self, objs, fields, batch_size=None):
        raise TypeError('Audit events are append-only.')

    def bulk_create(self, objs, *args, **kwargs):
        for obj in objs:
            obj.payload = redact(obj.payload)
        return super().bulk_create(objs, *args, **kwargs)


class AuditEventManager(models.Manager.from_queryset(AppendOnlyAuditQuerySet)):
    def append(self, *, payload=None, **fields):
        return self.create(payload=redact(payload or {}), **fields)


class AuditEvent(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        related_name='audit_events',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='v2_audit_events',
    )
    event_type = models.CharField(max_length=120)
    target_type = models.CharField(max_length=120)
    target_public_id = models.UUIDField(null=True, blank=True)
    correlation_id = models.CharField(max_length=128, blank=True)
    payload = models.JSONField(default=dict)
    occurred_at = models.DateTimeField(auto_now_add=True, editable=False)

    objects = AuditEventManager()

    class Meta:
        ordering = ('occurred_at', 'id')
        indexes = [
            models.Index(fields=('workspace', '-occurred_at'), name='audit_ws_time_idx'),
            models.Index(fields=('event_type', '-occurred_at'), name='audit_type_time_idx'),
            models.Index(fields=('target_type', 'target_public_id'), name='audit_target_idx'),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise TypeError('Audit events are append-only.')
        self.payload = redact(self.payload)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError('Audit events are append-only.')

    def __str__(self):
        return f'{self.event_type}:{self.public_id}'
