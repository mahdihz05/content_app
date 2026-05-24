from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):

    total_accounts = serializers.IntegerField()

    active_accounts = serializers.IntegerField()

    total_campaigns = serializers.IntegerField()

    active_campaigns = serializers.IntegerField()

    total_messages = serializers.IntegerField()