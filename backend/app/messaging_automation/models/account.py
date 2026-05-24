from django.db import models
from django.conf import settings

class MessagingAccount(models.Model):

    PLATFORM_CHOICES = [
        ("telegram", "Telegram"),
        ("whatsapp", "WhatsApp"),
        ("bale", "Bale"),
        ("rubika", "Rubika"),
        ("eitaa", "Eitaa"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    platform = models.CharField(
        max_length=30,
        choices=PLATFORM_CHOICES
    )

    name = models.CharField(max_length=255)

    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    session_path = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.name}"