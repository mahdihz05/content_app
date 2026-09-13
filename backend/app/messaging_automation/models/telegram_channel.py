import uuid

from django.db import models
from django.contrib.auth import get_user_model
from campaigns.models import Campaign


class TelegramChannel(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_telegram_channels',
    )

    CHANNEL_TYPE_CHOICES = [
        ("channel", "Channel"),
        ("supergroup", "Supergroup"),
        ("group", "Group"),
    ]

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="telegram_channels"
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="telegram_channels"
    )

    chat_id = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)
    channel_type = models.CharField(
        max_length=50,
        choices=CHANNEL_TYPE_CHOICES,
        default="channel"
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "chat_id")

    def __str__(self):
        return self.title
