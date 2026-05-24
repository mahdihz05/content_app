from django.contrib.auth.decorators import login_required
from rest_framework import status

from campaigns.models import Campaign
from utils.api_response import api_response
@login_required
def campaign_list(request):
    if request.method == 'GET':
        user = request.user
        list = []
        try:
            campaigns = Campaign.objects.filter(user=user).all().order_by('-id')
            for campaign in campaigns:\
                list.append({
                    "id":campaign.id,
                    "title":campaign.title,
                    "main_keywords":campaign.main_keyword,
                    "status":campaign.status,
                })
            return api_response(success=True,
                                message="Campaign List",
                                data=list,
                                status_code=status.HTTP_200_OK)
        except Exception as e:
            return api_response(success=False,
                                error=e,
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)