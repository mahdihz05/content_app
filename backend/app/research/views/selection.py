from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from utils.api_response import api_response
from research.models import ResearchSource
from django.contrib.auth.decorators import login_required
from workspaces.access import workspace_object_or_404
from workspaces.policy import Actions


@csrf_exempt
@login_required
def select_source(request, source_id):
    if request.method != "POST":
        return api_response(False, error="Invalid method", status_code=405)

    source = workspace_object_or_404(
        request, ResearchSource, action=Actions.CONTENT_MUTATE, id=source_id
    )

    source.is_selected = True
    source.save()

    return api_response(True, message="Source selected", data={"id": source.id})
