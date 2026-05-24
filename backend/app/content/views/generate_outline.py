from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from content.models import ContentItem
from research.models import ResearchSource
import json
from utils.api_response import api_response
from ai.services.prompt_service import PromptService


class GenerateOutlineAPI(View):
    def post(self, request):
        try:
            body = json.loads(request.body.decode("utf-8"))
            content_id = body.get("content_id")

            if not content_id:
                return api_response(False, error="content_id is required", status_code=400)

            item = ContentItem.objects.filter(id=content_id).first()
            if not item:
                return api_response(False, error="ContentItem not found", status_code=404)

            # -----------------------------------------------------
            # تحقیق مرحله ۵
            # -----------------------------------------------------
            research_data = list(
                ResearchSource.objects.filter(content_item=item)
                .values("id", "summary", "raw_text")
            )

            # تبدیل به JSON برای استفاده در پرامپت واقعی
            merged_research_json = json.dumps(research_data, ensure_ascii=False)

            # -----------------------------------------------------
            # ساختن پرامپت اوت‌لاین (برای استفاده LLM واقعی در آینده)
            # -----------------------------------------------------
            outline_prompt = PromptService.get_outline_prompt(
                topic_title=item.title,
                main_keyword=item.main_keyword,
                merged_research_json=merged_research_json,
                language=item.language or "Persian"
            )

            # اینجا فعلاً ایمپلیمنتیشن تو عوض نشد.
            # بعداً می‌تونی LLM سرویس را اضافه کنی:
            #
            # llm_response = call_llm_api(outline_prompt)
            # outline = llm_response["outline"]
            #
            # فعلاً ماک نگه داشتیم تا عملکرد فعلی خراب نشود:

            outline = []

            outline.append({
                "title": "Introduction",
                "bulletPoints": [
                    f"Content Title: {item.title}",
                    f"Main Keyword: {item.main_keyword}",
                ]
            })
            outline.append({
                "title": "Key Insights",
                "bulletPoints": [
                    f"Research count: {len(research_data)}",
                    "Summaries extracted from research data"
                ]
            })
            outline.append({
                "title": "Conclusion",
                "bulletPoints": [
                    "Wrap-up",
                    "Call to action depending on goal"
                ]
            })

            # -----------------------------------------------------
            # ریترن نهایی مثل قبل + پرامپت اضافه شده
            # -----------------------------------------------------
            return api_response(
                True,
                message="Outline generated (mock mode)",
                data={
                    "outline": outline,
                    "prompt_used": outline_prompt,   # ← برای تست و بررسی
                }
            )

        except Exception as e:
            return api_response(False, error=str(e), status_code=500)
