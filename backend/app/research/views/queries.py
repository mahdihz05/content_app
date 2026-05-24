from django.shortcuts import get_object_or_404
from utils.api_response import api_response
from ai.services.prompt_service import PromptService
from content.models import ContentItem
from django.views.decorators.csrf import csrf_exempt
import json
from research.models import ResearchSource
from ai.services.ai_text_service import AITextService

@csrf_exempt
def generate_search_queries(request, content_id):
    if request.method != "POST":
        return api_response(False, error="Invalid method", status_code=405)

    content_item = get_object_or_404(ContentItem, id=content_id)

    try:
        body = json.loads(request.body or "{}")
    except Exception:
        body = {}

    # تعداد query ها
    count = body.get("count", 5)

    # query های قبلی برای جلوگیری از تکرار
    existing_queries = body.get("existing_queries", [])

    prompt = PromptService.get_search_queries_prompt(
        topic_title=content_item.title,
        main_keyword=content_item.main_keyword,
        language="Persian",
        count=count,
        existing_queries=existing_queries
    )

    response = AITextService.generate(prompt=prompt, message='generating queries')

    try:
        data = json.loads(response)
    except Exception:
        return api_response(False, error=f"Invalid AI response: {response}", status_code=500)

    queries = data.get("queries", [])

    created = []

    for q in queries:
        src = ResearchSource.objects.create(
            content_item=content_item,
            title=q,
            summary="",
            raw_text="",
            is_selected=False,
            source_type="ai",
        )

        created.append({
            "id": src.id,
            "title": src.title
        })

    return api_response(
        True,
        message="Search queries generated",
        data={"queries": created}
    )
