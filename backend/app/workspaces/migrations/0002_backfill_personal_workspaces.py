import uuid

from django.conf import settings
from django.db import migrations
from django.utils.text import slugify


def backfill_personal_workspaces(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label, model_name)
    Workspace = apps.get_model('workspaces', 'Workspace')
    Membership = apps.get_model('workspaces', 'WorkspaceMembership')

    existing_users = set(Membership.objects.values_list('user_id', flat=True))
    for user in User.objects.exclude(pk__in=existing_users).iterator():
        name = getattr(user, 'name', None) or 'Personal workspace'
        suffix = uuid.uuid4().hex[:10]
        workspace = Workspace.objects.create(
            public_id=uuid.uuid4(),
            name=name,
            slug=f'{slugify(name) or "workspace"}-{suffix}',
            created_by_id=user.pk,
        )
        Membership.objects.create(
            workspace=workspace,
            user_id=user.pk,
            role='owner',
            is_active=True,
            is_default=True,
        )


class Migration(migrations.Migration):
    dependencies = [('workspaces', '0001_initial')]

    operations = [
        migrations.RunPython(backfill_personal_workspaces, migrations.RunPython.noop),
    ]
