from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from content.models import ContentItem, ContentForm
from research.models import ResearchSource
from utils.api_response import api_response
from ai.services.prompt_service import PromptService
from ai.services.ai_text_service import AITextService

@method_decorator(csrf_exempt, name="dispatch")
class GenerateFinalContentAPI(View):

    def post(self, request):
        try:
            body = json.loads(request.body.decode("utf-8"))
            content_id = body.get("content_id")

            if not content_id:
                return api_response(False, error="content_id is required", status_code=400)

            # -------------------------------------------------------------------
            # Load ContentItem
            # -------------------------------------------------------------------
            item = ContentItem.objects.filter(id=content_id).first()
            if not item:
                return api_response(False, error="ContentItem not found", status_code=404)

            # -------------------------------------------------------------------
            # Load ContentForm
            # -------------------------------------------------------------------
            form = getattr(item, "content_form", None)
            if not form:
                return api_response(False, error="ContentForm not found for this content item", status_code=404)

            form_data = form.data or {}

            # -------------------------------------------------------------------
            # Merge Research Data
            # -------------------------------------------------------------------
            research_items = ResearchSource.objects.filter(content_item=item)
            research_data = [
                {"summary": r.summary, "content": r.raw_text}
                for r in research_items
            ]

            merged_research_json = json.dumps(research_data, ensure_ascii=False)

            # -------------------------------------------------------------------
            # Update → generating
            # -------------------------------------------------------------------
            item.status = "generating"
            item.save(update_fields=["status"])

            # -------------------------------------------------------------------
            # Final Prompt Construction
            # -------------------------------------------------------------------
            final_prompt = PromptService.get_final_content_prompt(
                title=item.title,
                main_keyword=item.main_keyword,
                additional_keywords_json=json.dumps(item.additional_keywords or [], ensure_ascii=False),
                description=item.description or "",
                goal=item.goal or "",
                language=item.language or "fa",
                writer_persona=form_data.get("writer_persona", "نویسنده حرفه‌ای محتوا"),
                target_length=form_data.get("target_length", 1200),
                information_json=json.dumps(item.information or {}, ensure_ascii=False),
                merged_research_json=merged_research_json
            )

            # -------------------------------------------------------------------
            # Call LLM
            # -------------------------------------------------------------------
            llm_response_raw = AITextService.generate(prompt=final_prompt, message='generate final output')
            # Model may return string or JSON
            try:
                if isinstance(llm_response_raw, str):
                    llm_response = json.loads(llm_response_raw)
                else:
                    llm_response = llm_response_raw
            except json.JSONDecodeError:
                llm_response = {"html": llm_response_raw, "meta": {}, "images": []}

            # -------------------------------------------------------------------
            # Update → completed
            # -------------------------------------------------------------------
            item.status = "completed"
            item.save(update_fields=["status"])

            # -------------------------------------------------------------------s
            # Return Response
            # -------------------------------------------------------------------
            return api_response(
                True,
                message="Final content generated successfully",
                data={
                    "content": llm_response,
                    "prompt_used": final_prompt
                }
            )

        except Exception as e:
            item = locals().get("item", None)
            if item:
                item.status = "idle"
                item.save(update_fields=["status"])
            return api_response(False, error=str(e), status_code=500)
