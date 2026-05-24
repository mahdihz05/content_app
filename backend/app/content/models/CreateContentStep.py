from django.db import models
from content.models import ContentItem

class CreateContentStep(models.Model):
    title = models.CharField(max_length=100)
    priority = models.IntegerField()
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
