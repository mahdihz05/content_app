from django.contrib.auth.decorators import login_required
from rest_framework import status

from utils.api_response import api_response
from campaigns.models import Campaign
from content.models import ContentItem


@login_required
def get_content_items(request):
    if request.method == 'GET':
        user = request.user
        campaign_id = request.GET.get('campaign_id')

        if campaign_id is not None:
            campaigns = Campaign.objects.filter(id=campaign_id, user=user)
        else:
            campaigns = Campaign.objects.filter(user=user).order_by('-created_at')

        result = []

        for campaign in campaigns:
            content_items = ContentItem.objects.filter(campaign=campaign)

            items = []
            for c in content_items:
                items.append({
                    'id': c.id,
                    'title': c.title,
                    'main_keyword': c.main_keyword,
                    'additional_keywords': c.additional_keywords,
                    'description': c.description,
                    'goal': c.goal,
                    'platform': c.platform,
                    'language': c.language,
                    'status': c.status,
                })

            result.append({
                'campaign_id': campaign.id,
                'campaign_title': campaign.title,
                'items': items,
            })

        return api_response(
            success=True,
            data=result,
            message='items founded successfully',
            status_code=status.HTTP_200_OK
        )

    return api_response(
        success=False,
        error='method not allowed',
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )
