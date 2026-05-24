import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from messaging_automation.models.account import (
    MessagingAccount
)

from messaging_automation.models.campaign import (
    Campaign
)

from messaging_automation.models import (
    CampaignRecipient
)

from messaging_automation.workers.campaign_worker import (
    CampaignWorker
)


class BulkSendCreateAPIView(APIView):

    def post(self, request):

        account_id = request.data.get(
            "account_id"
        )

        message = request.data.get(
            "message",
            ""
        )

        recipients_json = request.data.get(
            "recipients_json",
            "[]"
        )

        delay = request.data.get(
            "delay",
            2
        )

        try:

            account = MessagingAccount.objects.get(
                id=account_id,
                user=request.user
            )

        except MessagingAccount.DoesNotExist:

            return Response(
                {
                    "account_id": [
                        "اکانت پیدا نشد"
                    ]
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:

            recipients = json.loads(
                recipients_json
            )

        except:

            return Response(
                {
                    "recipients_json": [
                        "فرمت recipients نامعتبر است"
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not recipients:

            return Response(
                {
                    "recipients_json": [
                        "حداقل یک مخاطب وارد کنید"
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign = Campaign.objects.create(
            account=account,
            name=f"Bulk Campaign {account.id}",
            campaign_type="bulk",
            message=message,
            delay_between_messages=int(delay),
            status="draft",
        )

        for recipient in recipients:

            CampaignRecipient.objects.create(
                campaign=campaign,
                recipient=recipient
            )

        CampaignWorker.start_campaign(
            campaign
        )

        return Response(
            {
                "detail": "کمپین با موفقیت شروع شد",
                "campaign_id": campaign.id,
            },
            status=status.HTTP_201_CREATED
        )