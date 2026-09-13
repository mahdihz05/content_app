from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .context import resolve_workspace_context
from .policy import evaluate_policy


def require_workspace_action(request, action):
    context = resolve_workspace_context(request)
    if not evaluate_policy(context.membership, action).allowed:
        raise PermissionDenied
    return context


def workspace_object_or_404(request, model, *, action, **lookup):
    context = require_workspace_action(request, action)
    return get_object_or_404(model, workspace=context.workspace, **lookup)
