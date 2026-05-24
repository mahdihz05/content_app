from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from messaging_automation.models.campaign import Campaign

from messaging_automation.serializers.campaign_serializer import (
    CampaignSerializer
)


class CampaignListAPIView(APIView):

    def get(self, request):

        campaigns = Campaign.objects.all().order_by("-id")

        serializer = CampaignSerializer(
            campaigns,
            many=True
        )

        return Response(serializer.data)


class CampaignCreateAPIView(APIView):

    def post(self, request):

        serializer = CampaignSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CampaignDetailAPIView(APIView):

    def get(self, request, campaign_id):

        try:

            campaign = Campaign.objects.get(
                id=campaign_id
            )

        except Campaign.DoesNotExist:

            return Response(
                {"error": "Campaign not found"},
                status=404
            )

        serializer = CampaignSerializer(campaign)

        return Response(serializer.data)