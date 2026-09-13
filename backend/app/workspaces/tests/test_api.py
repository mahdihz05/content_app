from django.test import override_settings

from workspaces.models import WorkspaceMembership

from .base import WorkspaceTestCase


@override_settings(ROOT_URLCONF='workspaces.urls')
class WorkspaceAPITests(WorkspaceTestCase):
    def setUp(self):
        self.owner, self.owner_membership = self.create_user('Owner')
        self.target, self.target_default = self.create_user('Target')

    def test_workspace_apis_require_authentication(self):
        for url in ('/workspace/', '/workspaces/', '/workspace/members/'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 401)

    def test_current_context_and_membership_listing(self):
        self.client.force_login(self.owner)
        current = self.client.get('/workspace/')
        self.assertEqual(current.status_code, 200)
        self.assertEqual(
            current.json()['workspace']['public_id'],
            str(self.owner_membership.workspace.public_id),
        )
        memberships = self.client.get('/workspaces/')
        self.assertEqual(memberships.status_code, 200)
        self.assertEqual(len(memberships.json()['memberships']), 1)

    def test_switch_rejects_workspace_without_active_membership(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            '/workspace/switch/',
            {'workspace_id': str(self.target_default.workspace.public_id)},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error']['code'], 'workspace_access_denied')

    def test_switch_can_persist_a_new_default(self):
        membership = WorkspaceMembership.objects.create(
            workspace=self.target_default.workspace,
            user=self.owner,
            role=WorkspaceMembership.Role.VIEWER,
        )
        self.client.force_login(self.owner)
        response = self.client.post(
            '/workspace/switch/',
            {
                'workspace_id': str(membership.workspace.public_id),
                'make_default': True,
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        membership.refresh_from_db()
        self.owner_membership.refresh_from_db()
        self.assertTrue(membership.is_default)
        self.assertFalse(self.owner_membership.is_default)

    def test_owner_can_add_and_update_member(self):
        self.client.force_login(self.owner)
        created = self.client.post(
            '/workspace/members/',
            {'user_id': self.target.pk, 'role': 'editor'},
            content_type='application/json',
        )
        self.assertEqual(created.status_code, 201)
        membership_id = created.json()['id']
        updated = self.client.patch(
            f'/workspace/members/{membership_id}/',
            {'role': 'contributor'},
            content_type='application/json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()['role'], 'contributor')

    def test_admin_cannot_assign_or_modify_owner(self):
        admin_user, admin_default = self.create_user('Admin')
        admin = WorkspaceMembership.objects.create(
            workspace=self.owner_membership.workspace,
            user=admin_user,
            role=WorkspaceMembership.Role.ADMIN,
        )
        self.client.force_login(admin_user)
        session = self.client.session
        session['workspace_public_id'] = str(admin.workspace.public_id)
        session.save()

        create_response = self.client.post(
            '/workspace/members/',
            {'user_id': self.target.pk, 'role': 'owner'},
            content_type='application/json',
        )
        self.assertEqual(create_response.status_code, 400)
        owner_response = self.client.patch(
            f'/workspace/members/{self.owner_membership.pk}/',
            {'role': 'viewer'},
            content_type='application/json',
        )
        self.assertEqual(owner_response.status_code, 400)

    def test_last_active_owner_cannot_be_deleted(self):
        self.client.force_login(self.owner)
        response = self.client.delete(
            f'/workspace/members/{self.owner_membership.pk}/'
        )
        self.assertEqual(response.status_code, 400)
        self.owner_membership.refresh_from_db()
        self.assertTrue(self.owner_membership.is_active)

    def test_non_admin_role_cannot_list_or_administer_members(self):
        viewer_user, viewer_default = self.create_user('Viewer')
        viewer = WorkspaceMembership.objects.create(
            workspace=self.owner_membership.workspace,
            user=viewer_user,
            role=WorkspaceMembership.Role.VIEWER,
        )
        self.client.force_login(viewer_user)
        session = self.client.session
        session['workspace_public_id'] = str(viewer.workspace.public_id)
        session.save()
        self.assertEqual(self.client.get('/workspace/members/').status_code, 403)
        self.assertEqual(
            self.client.patch(
                f'/workspace/members/{viewer.pk}/',
                {'role': 'editor'},
                content_type='application/json',
            ).status_code,
            403,
        )
