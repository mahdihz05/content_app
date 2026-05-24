from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from utils.api_response import api_response
from content.models import ContentItem


@csrf_exempt
def finalize_research(request, content_id):
    if request.method != "POST":
        return api_response(False, error="Invalid method", status_code=405)

    content_item = get_object_or_404(ContentItem, id=content_id)

    sources = content_item.research_sources.filter(is_selected=True)

    final_list = []
    for src in sources:
        final_list.append({
            "id": src.id,
            "title": src.title,
            "summary": src.summary,
            "raw_text": src.raw_text
        })

    # Save inside the content_item.information (JSON field)
    content_item.information = {
        "research": final_list
    }
    content_item.status = "research_done"
    content_item.save()

    return api_response(True, message="Research finalized", data={"research": final_list})
