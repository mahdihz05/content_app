from django.db import models
from .account import MessagingAccount


class Campaign(models.Model):

    TYPE_CHOICES = [
        ("bulk", "Bulk"),
        ("auto_reply", "Auto Reply"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("running", "Running"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    ]

    account = models.ForeignKey(
        MessagingAccount,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    campaign_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES
    )

    message = models.TextField()

    ai_prompt = models.TextField(
        blank=True,
        null=True
    )

    delay_between_messages = models.IntegerField(default=5)

    max_messages_per_day = models.IntegerField(default=100)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name