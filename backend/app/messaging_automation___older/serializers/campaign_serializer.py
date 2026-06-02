from rest_framework import serializers

from messaging_automation.models.campaign import Campaign


class CampaignSerializer(serializers.ModelSerializer):

    account_name = serializers.CharField(
        source="account.name",
        read_only=True
    )

    class Meta:
        model = Campaign

        fields = [
            "id",
            "name",
            "campaign_type",
            "message",
            "status",
            "delay_between_messages",
            "max_messages_per_day",
            "created_at",
            "account",
            "account_name",
        ]