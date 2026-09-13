import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from campaigns.models import Campaign, CampaignGoal
from utils.api_response import api_response
from rest_framework import status
from platforms.models import Platform
from workspaces.access import require_workspace_action, workspace_object_or_404
from workspaces.policy import Actions


@csrf_exempt
@login_required()
def create_campaign(request):

    if request.method != "POST":
        return api_response(
            success=False,
            message="method not allowed",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    context = require_workspace_action(request, Actions.CONTENT_DRAFT)
    try:
        payload = json.loads(request.body)

        user = request.user

        title = payload.get("title")
        main_keyword = payload.get("main_keyword")
        goal_id = payload.get("goal")
        platform_id = payload.get("platform")
        description = payload.get("description", "")
        tag = payload.get("tag", "product")
        campaign_status = payload.get("status", "draft")
        settings = payload.get("settings", {})

        if not title or not main_keyword or not goal_id:
            return api_response(
                success=False,
                error="title, main_keyword and goal are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            goal = CampaignGoal.objects.get(id=goal_id)
        except CampaignGoal.DoesNotExist:
            return api_response(
                success=False,
                error="Invalid goal",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # اگر بعدا خواستی platform در Campaign ذخیره شود
        if platform_id:
            Platform.objects.filter(id=platform_id).first()

        campaign = Campaign.objects.create(
            user=user,
            workspace=context.workspace,
            title=title,
            main_keyword=main_keyword,
            description=description,
            tag=tag,
            status=campaign_status,
            goal=goal
        )

        # اینجا settings را می‌توانی در مدل جدا ذخیره کنی
        # مثلا CampaignSettings یا CampaignData
        # فعلا فقط برمی‌گردانیم

        return api_response(
            success=True,
            message="Campaign successfully created",
            data={
                "campaign_id": campaign.id,
                "settings": settings
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return api_response(
            success=False,
            error=f"Campaign creation failed: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
@login_required
def update_campaign(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        campaign_id = payload.get('campaign_id')
        if not campaign_id :
            return api_response(success=False,
                                error='Campaign id is required',
                                status_code=status.HTTP_400_BAD_REQUEST)
        campaign = workspace_object_or_404(
            request,
            Campaign,
            action=Actions.CONTENT_MUTATE,
            id=campaign_id,
        )
        campaign.status = payload.get('status')
        campaign.save()
        return api_response(success=True,
                            message='Campaign successfully updated',
                            status_code=status.HTTP_200_OK)
    return api_response(success=False,
                        message='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )



@csrf_exempt
@login_required
def delete_campaign(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        campaign_id = payload.get('campaign_id')
        if not campaign_id :
            return api_response(success=False,
                                error='Campaign id is required',
                                status_code=status.HTTP_400_BAD_REQUEST)
        campaign = workspace_object_or_404(
            request,
            Campaign,
            action=Actions.CONTENT_DELETE,
            id=campaign_id,
        )
        campaign.delete()
        return api_response(success=True,
                            message='Campaign successfully deleted',
                            status_code=status.HTTP_200_OK)
    return api_response(success=False,
                        message='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )
