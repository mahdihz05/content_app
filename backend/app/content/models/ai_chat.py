import uuid

from django.db import models
from django.contrib.auth import get_user_model
from content.models import ContentItem
from campaigns.models import Campaign

class AIChatSession(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_ai_chat_sessions',
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)  # ✅ اضافه شد
    content_item = models.ForeignKey(ContentItem, on_delete=models.SET_NULL, null=True, blank=True)  # ✅ اضافه شد
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ اضافه شد

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AIMessage(models.Model):
    MESSAGE_TYPE_TEXT = 'text'
    MESSAGE_TYPE_IMAGE = 'image'
    MESSAGE_TYPE_CHOICES = [
        (MESSAGE_TYPE_TEXT, 'Text'),
        (MESSAGE_TYPE_IMAGE, 'Image'),
    ]

    session = models.ForeignKey(AIChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20)
    content = models.TextField(null=True, blank=True)  # ✅ اضافه شد
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default=MESSAGE_TYPE_TEXT
    )
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


    def __str__(self):
        return f"{self.role}: {self.content[:50] if self.content else 'Image'}"

