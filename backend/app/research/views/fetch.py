from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from ai.services.ai_text_service import AITextService
from utils.api_response import api_response
from research.models import ResearchSource
from ai.services.prompt_service import PromptService  # مسیر را با پروژه خود یکی کنید
from django.contrib.auth.decorators import login_required
from workspaces.access import workspace_object_or_404
from workspaces.policy import Actions

@csrf_exempt
@login_required
def fetch_source_data(request, source_id):
    if request.method != "POST":
        return api_response(False, error="Invalid method", status_code=405)

    source = workspace_object_or_404(
        request, ResearchSource, action=Actions.CONTENT_MUTATE, id=source_id
    )

    prompt = PromptService.get_fetch_source_data_prompt(query=source.title)

    response_text = AITextService.generate(prompt=prompt, message='simulate scraping ')

    try:
        data = json.loads(response_text)
    except Exception:
        cleaned = (
            response_text.replace("\u200c", "")
                         .replace("“", "\"")
                         .replace("”", "\"")
                         .replace("’", "'")
        )
        data = json.loads(cleaned)

    if not isinstance(data, dict) or "sources" not in data or "summary" not in data:
        return api_response(False, error="AI JSON missing required keys: sources/summary", status_code=500)

    if not isinstance(data.get("sources"), list) or len(data["sources"]) == 0:
        return api_response(False, error="AI JSON 'sources' must be a non-empty list", status_code=500)

    # ذخیره ساختاریافته
    try:
        source.sources_json = data.get("sources", [])
    except AttributeError:
        # اگر فیلد نداریم، fallback به ذخیره کل JSON در raw_text
        source.raw_text = json.dumps(data, ensure_ascii=False)

    # خلاصه
    summary_paragraph = data.get("summary", {}).get("paragraph", "")
    source.summary = summary_paragraph

    # اگر خواستی raw_html ها را هم در raw_text تجمیع کنی:
    if hasattr(source, "sources_json") and source.sources_json:
        try:
            combined_htmls = "\n\n".join(
                [s.get("raw_html", "") for s in source.sources_json if isinstance(s, dict)]
            )
            source.raw_text = combined_htmls
        except Exception:
            pass

    source.save()

    return api_response(True, message="Source data fetched", data={
        "id": source.id,
        "title": source.title,
        "sources": source.sources_json if hasattr(source, "sources_json") else None,
        "raw_text": source.raw_text,
        "summary": source.summary
    })
