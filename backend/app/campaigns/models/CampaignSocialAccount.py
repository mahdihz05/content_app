from django.db import models
from platforms.models import SocialAccount

class CampaignSocialAccount(models.Model):
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE)
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.social_account.name