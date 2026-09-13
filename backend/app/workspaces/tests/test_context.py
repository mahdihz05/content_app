from django.test import RequestFactory, override_settings

from workspaces.context import SESSION_WORKSPACE_KEY, resolve_workspace_context
from workspaces.context_processors import workspace_context
from workspaces.exceptions import WorkspaceAccessDenied, WorkspaceNotSelected
from workspaces.models import Workspace, WorkspaceMembership

from .base import WorkspaceTestCase


class WorkspaceContextTests(WorkspaceTestCase):
    def setUp(self):
        self.user, self.default = self.create_user()
        self.factory = RequestFactory()

    def request(self, header=None, session=None):
        extras = {'HTTP_X_WORKSPACE_ID': header} if header else {}
        request = self.factory.get('/', **extras)
        request.user = self.user
        request.session = session if session is not None else {}
        return request

    def test_default_membership_is_used_without_explicit_selection(self):
        context = resolve_workspace_context(self.request())
        self.assertEqual(context.membership, self.default)

    def test_header_takes_precedence_over_session(self):
        workspace = Workspace.objects.create(
            name='Second', slug='second', created_by=self.user
        )
        second = WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.user,
            role=WorkspaceMembership.Role.EDITOR,
        )
        request = self.request(
            header=str(workspace.public_id),
            session={SESSION_WORKSPACE_KEY: str(self.default.workspace.public_id)},
        )
        self.assertEqual(resolve_workspace_context(request).membership, second)

    def test_invalid_or_foreign_explicit_selection_never_falls_back(self):
        other_user, other = self.create_user()
        del other_user
        for selected in ('not-a-uuid', str(other.workspace.public_id)):
            with self.subTest(selected=selected), self.assertRaises(WorkspaceAccessDenied):
                resolve_workspace_context(self.request(header=selected))

    def test_missing_default_is_reported(self):
        self.default.is_default = False
        self.default.save()
        with self.assertRaises(WorkspaceNotSelected):
            resolve_workspace_context(self.request())

    @override_settings(V2_FEATURE_FLAGS=set())
    def test_context_processor_is_inert_when_feature_is_disabled(self):
        self.assertEqual(
            workspace_context(self.request()),
            {'workspace_context_enabled': False},
        )

    @override_settings(V2_FEATURE_FLAGS={'workspaces', 'content_history'})
    def test_context_processor_exposes_workspace_and_evaluated_features(self):
        context = workspace_context(self.request())
        self.assertTrue(context['workspace_context_enabled'])
        self.assertEqual(context['current_workspace'], self.default.workspace)
        self.assertTrue(context['workspace_features']['content_history'])
