from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from campaigns.models import CampaignGoal
from utils.api_response import api_response
from rest_framework import status

@csrf_exempt
@login_required
def get_goal_list(request):
    if request.method == 'GET':
        campaign_goals = CampaignGoal.objects.all()
        goal_list = []
        for campaign_goal in campaign_goals:
            goal_list.append({
                'id': campaign_goal.id,
                'goal': campaign_goal.goal,
                'short_description': campaign_goal.short_description,
                'description': campaign_goal.description,
            })

        return api_response(success=True,
                            message='Goal list successfully created.',
                            data=goal_list,
                            status_code=status.HTTP_201_CREATED)
    return api_response(success=False,
                        error='method not allowed.',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)