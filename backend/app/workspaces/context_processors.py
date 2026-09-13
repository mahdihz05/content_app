from django.conf import settings
from rest_framework.exceptions import APIException

from common.feature_flags import is_feature_enabled

from .context import resolve_workspace_context
from .models import WorkspaceMembership


def workspace_context(request):
    flag_name = getattr(settings, 'V2_WORKSPACE_FEATURE_FLAG', 'workspaces')
    if not is_feature_enabled(flag_name) or not getattr(request.user, 'is_authenticated', False):
        return {'workspace_context_enabled': False}
    try:
        context = resolve_workspace_context(request)
    except APIException:
        return {'workspace_context_enabled': True, 'current_workspace': None}

    configured_flags = getattr(settings, 'V2_FEATURE_FLAGS', set())
    return {
        'workspace_context_enabled': True,
        'current_workspace': context.workspace,
        'current_workspace_membership': context.membership,
        'available_workspaces': WorkspaceMembership.objects.filter(
            user=request.user,
            is_active=True,
        ).select_related('workspace'),
        'workspace_features': {
            name: is_feature_enabled(name, workspace=context.workspace)
            for name in configured_flags
        },
    }
