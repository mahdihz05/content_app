from rest_framework.views import APIView
from rest_framework.response import Response

from messaging_automation.models.account import MessagingAccount
from messaging_automation.models.campaign import Campaign
from messaging_automation.models.message_log import MessageLog


class DashboardStatsAPIView(APIView):

    def get(self, request):

        data = {
            "total_accounts":
                MessagingAccount.objects.count(),

            "active_accounts":
                MessagingAccount.objects.filter(
                    is_active=True
                ).count(),

            "total_campaigns":
                Campaign.objects.count(),

            "active_campaigns":
                Campaign.objects.filter(
                    status="running"
                ).count(),

            "total_messages":
                MessageLog.objects.count(),
        }

        return Response(data)