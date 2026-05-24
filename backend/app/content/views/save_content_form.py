import json
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import schema

from campaigns.models import Campaign
from utils.api_response import api_response
from content.models import ContentForm, ContentItem, ContentFormSchema
from platforms.models import Platform
from content.views import create_contentItem

@login_required
def save_content_form(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        platform_id = payload.get('platform_id')
        data = payload.get('form_data')
        content_item_id = payload.get('content_item_id')
        content_item = ContentItem.objects.filter(id=content_item_id).first()
        if not platform_id or not data or not content_item_id:
            return api_response(success=False,
                                error='campaign_id or platform_id or data is empty',
                                status_code=status.HTTP_400_BAD_REQUEST)
        if not content_item:
            return api_response(success=False,
                                error='content_item dose not exist',
                                status_code=status.HTTP_400_BAD_REQUEST)

        platform = Platform.objects.filter(id=platform_id).first()
        schema = ContentFormSchema.objects.filter(platform=platform).first()
        if not platform or not schema:
            return api_response(success=False,
                                error='platform or schema dose not exist',
                                status_code=status.HTTP_400_BAD_REQUEST)

        content_form = ContentForm.objects.create(
            content_item=content_item,
            schema=schema,
            data=data
        )

        return api_response(
            success=True,
            data={"content_form_id": content_form.id},
            status_code=status.HTTP_201_CREATED
        )
    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_400_BAD_REQUEST)