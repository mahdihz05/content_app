from django.db import models
from .campaign import Campaign


class MessageLog(models.Model):

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE
    )

    sender = models.CharField(max_length=255)

    receiver = models.CharField(max_length=255)

    message = models.TextField()

    response = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)