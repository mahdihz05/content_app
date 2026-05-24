from django.db import models
from campaigns.models import Campaign, CampaignFormSchema

class CampaignForm(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="forms")
    schema = models.ForeignKey(CampaignFormSchema, on_delete=models.PROTECT)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
