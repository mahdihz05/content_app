import uuid

from django.db import models
from content.models import ContentItem


class ResearchJob(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_research_jobs',
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    request_payload = models.JSONField(default=dict)
    response_payload = models.JSONField(default=dict)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
