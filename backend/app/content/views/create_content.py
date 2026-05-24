from rest_framework.views import APIView
from rest_framework.response import Response

from content.models import ContentItem


class CreateContentItemView(APIView):

    def post(self, request):

        content = ContentItem.objects.create(
            campaign_id=request.data["campaign_id"],
            step="basic_info",
            status="idle"
        )

        return Response({
            "content_id": content.id,
            "step": content.step
        })
