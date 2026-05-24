from django.db import models
from platforms.models import Platform


class ContentFormSchema(models.Model):

    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name="content_schemas"
    )
    version = models.IntegerField(default=1)
    schema = models.JSONField()
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["platform", "version"]
        ordering = ["-version"]

    def __str__(self):
        return f"{self.platform.name} schema v{self.version}"
