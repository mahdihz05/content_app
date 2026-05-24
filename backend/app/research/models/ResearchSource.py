from django.db import models
from content.models import ContentItem

class ResearchSource(models.Model):

    SOURCE_TYPE = [
        ("ai", "AI"),
        ("url", "URL"),
        ("manual", "Manual"),
    ]

    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="research_sources"
    )

    title = models.CharField(max_length=500)

    url = models.URLField(blank=True, null=True)

    summary = models.TextField()

    raw_text = models.TextField(blank=True, null=True)

    source_type = models.CharField(max_length=50, choices=SOURCE_TYPE)
    sources_json = models.JSONField(null=True, blank=True)
    is_selected = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
