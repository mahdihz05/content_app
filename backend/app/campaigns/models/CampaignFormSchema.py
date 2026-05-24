from django.db import models
from campaigns.models.CampaignGoal import CampaignGoal


class CampaignFormSchema(models.Model):
    goal = models.ForeignKey(CampaignGoal, on_delete=models.PROTECT)
    version = models.IntegerField(default=1)
    schema_json = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("goal", "version")

    def __str__(self):
        return f"{self.goal} v{self.version}"
