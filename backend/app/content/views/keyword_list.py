from django.contrib.auth.decorators import login_required
from rest_framework import status

from content.models import Keyword
from utils.api_response import api_response


@login_required
def keyword_list(request):

    if request.method != 'GET':
        return api_response(
            success=False,
            error='method not allowed',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    user = request.user
    campaign_id = request.GET.get('campaign_id')
    content_item_id = request.GET.get('content_item_id')

    try:

        keywords = Keyword.objects.filter(
            content_item__campaign__user=user
        )

        if campaign_id:
            keywords = keywords.filter(content_item__campaign__id=campaign_id)

        if content_item_id:
            keywords = keywords.filter(content_item__id=content_item_id)

        keywords = keywords.select_related(
            'content_item',
            'content_item__campaign'
        ).order_by('-id')

        result = []

        for k in keywords:
            result.append({
                'id': k.id,
                'campaign_id': k.content_item.campaign.id,
                'campaign_title': k.content_item.campaign.title,
                'content_item_id': k.content_item.id,
                'content_item_title': k.content_item.title,
                'keyword': k.keyword,
                'source': k.source,
                'is_proccessed': k.is_proccessed,
            })

        return api_response(
            success=True,
            message='keywords loaded successfully',
            data=result,
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return api_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
