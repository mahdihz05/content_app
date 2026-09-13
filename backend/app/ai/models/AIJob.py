import uuid

from django.db import models
from content.models import ContentItem
from django.conf import settings

class AIJob(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_ai_jobs',
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    JOB_TYPE = [
        ("keyword_suggestion", "Keyword Suggestion"),
        ("research", "Research"),
        ("outline", "Outline"),
        ("content_generation", "Content Generation"),
        ("image_generation", "Image Generation"),
        ("audio_transcription", "Audio Transcription"),
        ("ai_interview", "AI Interview"),
    ]

    MEDIA_TYPE = [
        ("text", "Text"),
        ("image", "Image"),
        ("audio", "Audio"),
        ("video", "Video"),
    ]

    STATUS = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    job_type = models.CharField(max_length=50, choices=JOB_TYPE)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE, default="text")

    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    parent_job = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sub_jobs"
    )

    status = models.CharField(max_length=50, choices=STATUS, default="pending")

    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
