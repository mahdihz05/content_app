from django.db import models
from ai.models import AIInterviewSession

class AIInterviewState(models.Model):
    session = models.OneToOneField(AIInterviewSession, on_delete=models.CASCADE, related_name="state")

    collected_data = models.JSONField(default=dict)
    missing_fields = models.JSONField(default=list)

    confidence_score = models.FloatField(default=0.0)
    current_question = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
