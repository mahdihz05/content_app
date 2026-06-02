from django.db import models
from .campaign import Campaign


class CampaignRecipient(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("replied", "Replied"),
    ]

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE
    )

    recipient = models.CharField(max_length=255)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending"
    )

    sent_at = models.DateTimeField(
        blank=True,
        null=True
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )