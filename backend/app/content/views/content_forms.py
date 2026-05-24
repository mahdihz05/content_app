from rest_framework.views import APIView
from rest_framework.response import Response

from content.models import ContentItem, ContentForm


class SaveContentFormView(APIView):

    def post(self, request):

        content_item = ContentItem.objects.get(id=request.data["content_id"])
        step = request.data["step"]
        data = request.data["data"]

        if step == "basic_info":

            content_item.title = data.get("title")
            content_item.description = data.get("description", "")
            content_item.step = "production_info"
            content_item.save()

        elif step == "production_info":

            content_item.goal = data.get("goal")
            content_item.platform = data.get("platform", "website")
            content_item.language = data.get("language", "fa")

            content_item.step = "keywords"
            content_item.save()

        elif step == "keywords":

            content_item.main_keyword = data.get("main_keyword")
            content_item.additional_keywords = data.get("additional_keywords", [])

            content_item.step = "research"
            content_item.status = "researching"
            content_item.save()

        elif step == "knowledge":

            form, _ = ContentForm.objects.get_or_create(
                content_item=content_item
            )

            form.data = data
            form.save()

            content_item.step = "approval"
            content_item.save()

        return Response({
            "step": content_item.step
        })
