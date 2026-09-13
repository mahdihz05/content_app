import uuid

from django.db import models
from campaigns.models.Campaign import Campaign


class ContentItem(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_content_items',
    )

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("idle", "Idle"),
        ("researching", "Researching"),
        ("research_done", "Research Done"),
        ("outlining", "Outlining"),
        ("outline_done", "Outline Done"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("scheduled", "Scheduled"),
        ("published", "Published"),
        ("publish_failed", "Publish Failed"),
    ]
    PUBLISH_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("queued", "Queued"),
        ("publishing", "Publishing"),
        ("published", "Published"),
        ("failed", "Failed"),
    ]
    step = models.CharField(
        max_length=50,
        default="research"
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200,
        default="untitled"
    )

    main_keyword = models.CharField(
        max_length=100,
        blank=True
    )

    additional_keywords = models.JSONField(
        default=list
    )

    description = models.TextField(
        blank=True
    )

    goal = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    platform = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    language = models.CharField(
        max_length=20,
        default="fa"
    )

    information = models.JSONField(
        null=True,
        blank=True
    )

    metadata = models.JSONField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="idle"
    )

    search_source = models.JSONField(
        null=True,
        blank=True
    )

    # ==========================================
    # AUTO PUBLISH
    # ==========================================

    auto_publish = models.BooleanField(
        default=False
    )

    publish_immediately = models.BooleanField(
        default=False
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    publish_status = models.CharField(
        max_length=50,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title
