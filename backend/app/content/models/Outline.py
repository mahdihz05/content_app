from django.db import models
from content.models import ContentItem

class Outline(models.Model):

    content_item = models.OneToOneField(ContentItem, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
