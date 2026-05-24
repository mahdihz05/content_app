from django.db import models


class DocumentEmbedding(models.Model):
    source = models.ForeignKey("KnowledgeSource", on_delete=models.CASCADE)
    chunk_text = models.TextField()
    embedding = models.JSONField()
    order = models.IntegerField(default=0)
