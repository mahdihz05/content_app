import json
from ai.services import AITextService
from django.contrib.auth.decorators import login_required
from rest_framework import status

from content.models import ContentItem, ContentForm
from utils.api_response import api_response
from ai.services.prompt_service import PromptService


@login_required
def generate_keyword(request):

    if request.method != "POST":
        return api_response(
            success=False,
            error="method not allowed",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        payload = json.loads(request.body)
    except Exception:
        return api_response(
            success=False,
            error="Invalid JSON body",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    content_id = payload.get("content_id")
    if not content_id:
        return api_response(
            success=False,
            error="Content id is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        content_item = ContentItem.objects.get(id=content_id)
    except ContentItem.DoesNotExist:
        return api_response(
            success=False,
            error=f"Content item with id {content_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    content_form_id = payload.get("content_form_id")
    if not content_form_id:
        return api_response(
            success=False,
            error="Content form id is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        content_form = ContentForm.objects.get(id=content_form_id)
    except ContentForm.DoesNotExist:
        return api_response(
            success=False,
            error=f"Content form with id {content_form_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    user_data = {
        "title": content_item.title,
        "campaign_title": content_item.campaign.title if content_item.campaign else None,
        "main_user_keyword": content_item.main_keyword,
        "user_additional_keywords": content_item.additional_keywords,
        "description": content_item.description,
        "content_goal": content_item.goal,
        "platform": str(content_item.platform),
        "language": content_item.language,
        "status": content_item.status,
        "form_data": content_form.data
    }

    try:
        ai_prompt = PromptService.get_keyword_generation_prompt(user_data)

        message = "Generate SEO keywords based on the provided content data."

        ai_response = AITextService.generate(message=message, prompt=ai_prompt)
        try:
            ai_response = json.loads(ai_response)
        except Exception:
            return api_response(
                success=False,
                error="AI returned invalid JSON",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        if not ai_response:
            return api_response(
                success=False,
                error="AI returned empty response",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return api_response(
            success=True,
            data=ai_response,
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return api_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
