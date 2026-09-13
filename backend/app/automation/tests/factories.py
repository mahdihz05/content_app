from django.db import models

from workspaces.models import Workspace, WorkspaceMembership


def create_workspace(owner, suffix='one'):
    """Supply conventional values while tolerating the separately delivered workspace model."""
    values = {}
    for field in Workspace._meta.concrete_fields:
        if field.primary_key or field.auto_created or field.has_default() or field.null:
            continue
        if isinstance(field, models.ForeignKey):
            values[field.name] = owner
        elif isinstance(field, models.CharField):
            values[field.name] = f'test-{field.name}-{suffix}'
        elif isinstance(field, models.BooleanField):
            values[field.name] = True
    workspace = Workspace.objects.create(**values)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=owner,
        role=WorkspaceMembership.Role.OWNER,
    )
    return workspace
