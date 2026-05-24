from django.db import models
from django.contrib.auth import get_user_model


class KnowledgeSource(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50)   # pdf, url, text
    created_at = models.DateTimeField(auto_now_add=True)
