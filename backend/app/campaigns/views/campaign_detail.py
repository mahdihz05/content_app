import json
from django.contrib.auth.decorators import login_required
from rest_framework import status
from campaigns.models import Campaign
from utils.api_response import api_response


@login_required
def campaign_detail(request):
    if request.method == 'GET':
        user = request.user
        campaign_id = request.GET.get('campaign_id')
        if not campaign_id:
            return api_response(success=False,
                                error='campaign_id is required',
                                status_code=status.HTTP_400_BAD_REQUEST)
        campaign = Campaign.objects.get(id=campaign_id)
        if not campaign:
            return api_response(success=False,
                                error='campaign not found',
                                status_code=status.HTTP_404_NOT_FOUND)
        data = {
            'id': campaign_id,
            'title': campaign.title,
            'main_keywords': campaign.main_keyword,
            'status': campaign.status,
            'created_at': campaign.created_at,
            'updated_at': campaign.updated_at,
        }
        return api_response(success=True,
                            message='campaign detail load successfully',
                            data=data,
                            status_code=status.HTTP_200_OK)

    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)