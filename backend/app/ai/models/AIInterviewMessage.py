from django.db import models
from ai.models import AIInterviewSession


class AIInterviewMessage(models.Model):
    session = models.ForeignKey(AIInterviewSession, on_delete=models.CASCADE, related_name="messages")

    ROLE = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System")
    ]

    role = models.CharField(max_length=20, choices=ROLE)
    content = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
