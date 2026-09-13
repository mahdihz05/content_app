import uuid

from django.db import models
from django.conf import settings
from ai.models import AIJob
from content.models import ContentItem

class AIInterviewSession(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_ai_interview_sessions',
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_item = models.ForeignKey(ContentItem, null=True, blank=True, on_delete=models.CASCADE)

    job = models.OneToOneField(AIJob, null=True, blank=True, on_delete=models.SET_NULL)

    status = models.CharField(max_length=20, default="active")  # active, completed, cancelled
    collected_data = models.JSONField(default=dict)             # extracted info
    missing_fields = models.JSONField(default=list)             # fields AI still needs
    stage = models.CharField(max_length=50, default="start")    # future: research / brief / outline

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
