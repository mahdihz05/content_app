from rest_framework.views import APIView
from rest_framework.response import Response

from content.models import ContentItem, ContentForm
from ai.pipelines.create_content.core import CreateContentCore


class ContentWorkflowView(APIView):

    def post(self, request):

        content_id = request.data.get("content_id")

        content_item = ContentItem.objects.get(id=content_id)

        context = {
            "content_item": content_item,
            "data": request.data
        }

        result = CreateContentCore().run(context)

        return Response({
            "step": content_item.step,
            "status": content_item.status,
            "result": result
        })
