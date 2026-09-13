from django.contrib.auth import get_user_model
from django.test import TestCase

from workspaces.models import WorkspaceMembership


class WorkspaceTestCase(TestCase):
    user_counter = 0

    def create_user(self, name=None):
        type(self).user_counter += 1
        user = get_user_model().objects.create_user(
            phone_number=f'0912{type(self).user_counter:07d}',
            password='test-password',
            name=name,
        )
        membership = WorkspaceMembership.objects.select_related('workspace').get(
            user=user,
            is_default=True,
        )
        return user, membership
