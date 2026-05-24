from django.db import models
from content.models import ContentItem

class GeneratedContent(models.Model):

    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name="generations")

    content_text = models.TextField()

    model_used = models.CharField(max_length=100)

    rag_context_used = models.JSONField(default=dict)

    generation_metadata = models.JSONField(default=dict)

    version = models.IntegerField(default=1)

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
