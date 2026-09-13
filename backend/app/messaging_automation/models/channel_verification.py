import random
import string
import uuid
from django.db import models
from django.contrib.auth import get_user_model


def generate_token():
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=6))
    return f"ABRIT-{suffix}"


class ChannelVerification(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_channel_verifications',
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="channel_verifications"
    )

    token = models.CharField(
        max_length=20,
        unique=True,
        default=generate_token
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.token}"
