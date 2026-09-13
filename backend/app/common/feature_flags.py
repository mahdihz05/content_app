from django.conf import settings


def is_feature_enabled(name, workspace=None):
    """Return a fail-closed flag value with optional workspace policy overrides."""
    if name not in getattr(settings, 'V2_FEATURE_FLAGS', set()):
        return False
    if workspace is None:
        return True

    from workspaces.models import WorkspaceFeatureFlag

    override = WorkspaceFeatureFlag.objects.filter(
        workspace=workspace,
        name=name,
    ).values_list('is_enabled', flat=True).first()
    return True if override is None else override
