from django.db import models
from content.models import ContentItem


class Keyword(models.Model):

    SOURCE_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]

    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="keywords"
    )

    keyword = models.CharField(max_length=200)

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)

    is_selected = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keyword
