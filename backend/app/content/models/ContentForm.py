from django.db import models
from content.models import ContentItem, ContentFormSchema


class ContentForm(models.Model):
    content_item = models.OneToOneField(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="content_form"
    )
    schema = models.ForeignKey(
        ContentFormSchema,
        on_delete=models.PROTECT,
        related_name="forms",
        null=True,
        blank=True
    )
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Form for Content {self.content_item_id}"