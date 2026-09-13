from django.conf import settings


def is_feature_enabled(name, workspace=None):
    """Return a fail-closed flag value; workspace support is added in Phase 1."""
    del workspace
    return name in getattr(settings, 'V2_FEATURE_FLAGS', set())
