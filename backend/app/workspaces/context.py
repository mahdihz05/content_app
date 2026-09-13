import uuid
from dataclasses import dataclass

from django.db import transaction

from .exceptions import WorkspaceAccessDenied, WorkspaceNotSelected
from .models import WorkspaceMembership


SESSION_WORKSPACE_KEY = 'workspace_public_id'
WORKSPACE_HEADER = 'X-Workspace-ID'


@dataclass(frozen=True)
class WorkspaceContext:
    workspace: object
    membership: WorkspaceMembership


def _selected_public_id(request):
    header_value = request.headers.get(WORKSPACE_HEADER)
    if header_value:
        return header_value
    return request.session.get(SESSION_WORKSPACE_KEY)


def resolve_workspace_context(request, *, refresh=False):
    if not refresh and hasattr(request, 'workspace_context'):
        return request.workspace_context
    if not getattr(request.user, 'is_authenticated', False):
        raise WorkspaceAccessDenied('Authentication is required to select a workspace.')

    memberships = WorkspaceMembership.objects.select_related('workspace').filter(
        user=request.user,
        is_active=True,
    )
    selected = _selected_public_id(request)
    if selected:
        try:
            selected = uuid.UUID(str(selected))
        except (TypeError, ValueError, AttributeError):
            raise WorkspaceAccessDenied() from None
        membership = memberships.filter(workspace__public_id=selected).first()
        if membership is None:
            raise WorkspaceAccessDenied()
    else:
        membership = memberships.filter(is_default=True).first()
        if membership is None:
            raise WorkspaceNotSelected()

    context = WorkspaceContext(membership.workspace, membership)
    request.workspace = context.workspace
    request.workspace_membership = context.membership
    request.workspace_context = context
    return context


def select_workspace(request, public_id, *, make_default=False):
    try:
        public_id = uuid.UUID(str(public_id))
    except (TypeError, ValueError, AttributeError):
        raise WorkspaceAccessDenied() from None

    with transaction.atomic():
        user_memberships = list(
            WorkspaceMembership.objects.select_for_update()
            .select_related('workspace')
            .filter(user=request.user)
            .order_by('pk')
        )
        membership = next(
            (
                item
                for item in user_memberships
                if item.workspace.public_id == public_id and item.is_active
            ),
            None,
        )
        if membership is None:
            raise WorkspaceAccessDenied()

        if make_default and not membership.is_default:
            WorkspaceMembership.objects.filter(user=request.user, is_default=True).update(
                is_default=False
            )
            membership.is_default = True
            membership.save(update_fields=('is_default', 'updated_at'))
    request.session[SESSION_WORKSPACE_KEY] = str(membership.workspace.public_id)
    return membership
