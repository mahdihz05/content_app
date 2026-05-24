from django.contrib.auth.decorators import login_required
from campaigns.models import CampaignGoal, CampaignFormSchema
from utils.api_response import api_response
from rest_framework import status


@login_required
def get_all_goal_schema(request):
    if request.method != "GET":
        return api_response(
            success=False,
            error="method not allowed",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    schemas = CampaignFormSchema.objects.select_related("goal").all()

    result = []
    for s in schemas:
        result.append({
            "id": s.id,
            "goal": s.goal.goal,
            "version": s.version,
            "schema": s.schema_json,
            "is_active": s.is_active,
        })

    return api_response(
        success=True,
        message="all schemas returned",
        data=result,
        status_code=status.HTTP_200_OK
    )


@login_required
def get_goal_schema(request):
    if request.method != "GET":
        return api_response(
            success=False,
            error="method not allowed",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    goal_id = request.GET.get("goal_id")

    if not goal_id:
        return api_response(
            success=False,
            error="goal_id not provided",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    schema = (
        CampaignFormSchema.objects
        .filter(goal_id=goal_id, is_active=True)
        .order_by("-version")
        .first()
    )

    if not schema:
        return api_response(
            success=False,
            error="schema not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    result = {
        "id": schema.id,
        "goal": schema.goal.goal,
        "version": schema.version,
        "schema": schema.schema_json,
        "is_active": schema.is_active,
    }

    return api_response(
        success=True,
        message="schema returned successfully",
        data=result,
        status_code=status.HTTP_200_OK
    )
