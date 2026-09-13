import uuid

from django.db import models
from content.models import ContentItem
from .telegram_channel import TelegramChannel


class TelegramPublishLog(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_telegram_publish_logs',
    )

    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE
    )

    channel = models.ForeignKey(
        TelegramChannel,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES
    )

    response_json = models.JSONField(
        null=True,
        blank=True
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
