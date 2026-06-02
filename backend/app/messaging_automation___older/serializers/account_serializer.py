from rest_framework import serializers

from messaging_automation.models.account import MessagingAccount


class MessagingAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = MessagingAccount

        fields = [
            "id",
            "platform",
            "name",
            "phone",
            "is_active",
            "created_at"
        ]