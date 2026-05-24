from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import status
from rest_framework.generics import get_object_or_404

from campaigns.models import Campaign
from utils.api_response import api_response
from content.models import ContentItem


@csrf_exempt
@login_required
def create_contentItem(request):
    if request.method == 'POST':
        user = request.user
        payload = json.loads(request.body)
        campaign_id = payload.get('campaign_id')
        if campaign_id is None:
            return api_response(success=False,
                                error='campaign_id is required',
                                status_code=status.HTTP_400_BAD_REQUEST)
        campaign = Campaign.objects.get(id=campaign_id)
        if campaign is None:
            return api_response(success=False,
                                error='campaign not found',
                                status_code=status.HTTP_404_NOT_FOUND)

        title = payload.get('title')
        main_keyword = payload.get('main_keyword')
        additional_keywords = payload.get('additional_keywords')
        description = payload.get('description')
        goal = payload.get('goal')
        platform = payload.get('platform')
        language = payload.get('language')
        if not title or not main_keyword:
            return api_response(success=False,
                                error='title and main_keyword is required',
                                status_code=status.HTTP_400_BAD_REQUEST)
        content_item = ContentItem.objects.create(
            campaign=campaign,
            title=title,
            main_keyword=main_keyword,
            additional_keywords=additional_keywords,
            description=description,
            goal=goal,
            platform=platform,
            language=language,
        )
        return api_response(
            success=True,
            data={
                "content_item_id": content_item.id
            },
            message='content item created successfully',
            status_code=status.HTTP_201_CREATED
        )
    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@login_required
def update_contentItem(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return api_response(
                success=False,
                error='Invalid JSON',
                status_code=400
            )

        contentItem_id = payload.get('contentItem_id')
        if contentItem_id is None:
            return api_response(success=False,
                                error='contentItem_id is required',
                                status_code=status.HTTP_400_BAD_REQUEST)
        content_item = get_object_or_404(ContentItem, id=contentItem_id)
        if not content_item:
            return api_response(
                success=False,
                error='ContentItem not found',
                status_code=404
            )

        fields = [
            "title",
            "main_keyword",
            "additional_keywords",
            "description",
            "goad",
            "platform",
            "language",
        ]
    
        for field in fields:
            if field in payload:
                setattr(content_item, field, payload[field])

        content_item.save()

        return api_response(
            success=True,
            data={"message": "ContentItem updated successfully"},
            status_code=200
        )
    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@login_required
def delete_contentItem(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        contentItem_id = payload.get('contentItem_id')
        content_item = get_object_or_404(ContentItem, id=contentItem_id)
        if not content_item:
            return api_response(success=False,
                                error='ContentItem not found',
                                status_code=status.HTTP_404_NOT_FOUND)
        content_item.delete()
        return api_response(success=True,
                            message='ContentItem deleted successfully',
                            status_code=status.HTTP_204_NO_CONTENT)
    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)





@csrf_exempt
@login_required
def add_source_to_content_item(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        sources = data.get('selected_kb', [])
        content_id = data.get('contentItem_id')

        form_obj = get_object_or_404(ContentItem, id=content_id)
        form_obj.search_source = sources
        form_obj.save()
        return api_response(success=True,
                            message='Source added successfully',
                            status_code=status.HTTP_201_CREATED)
    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
