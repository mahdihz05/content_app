from django.db import models

class CampaignGoal(models.Model):
    id = models.AutoField(primary_key=True)
    goal = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")