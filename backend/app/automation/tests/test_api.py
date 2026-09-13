from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from automation.registry import PolicyDecision, ToolRegistry, ToolSpec
from automation.services import create_command, request_approval
from automation.tests.factories import create_workspace
from user.models import CustomUser
from workspaces.models import WorkspaceMembership


@override_settings(ROOT_URLCONF='automation.urls')
class InternalStatusApiTests(TestCase):
    def setUp(self):
        self.actor = CustomUser.objects.create_user('09120000071', 'password')
        self.other = CustomUser.objects.create_user('09120000072', 'password')
        self.reviewer = CustomUser.objects.create_superuser('09120000073', 'password')
        self.workspace = create_workspace(self.actor, 'api')
        WorkspaceMembership.objects.create(
            workspace=self.workspace,
            user=self.reviewer,
            role=WorkspaceMembership.Role.ADMIN,
        )
        registry = ToolRegistry()
        registry.register(ToolSpec(
            'test.read', '1', 'read', 'test.read', '1',
            {'type': 'object'}, {'type': 'object'},
        ))
        preflight = registry.preflight(
            name='test.read', version='1', payload={}, actor=self.actor, workspace=self.workspace,
            policy_evaluator=lambda **kwargs: PolicyDecision(True, False, '1'),
        )
        self.command, _ = create_command(
            workspace=self.workspace, actor=self.actor, idempotency_key='api-command',
            preflight=preflight, payload={},
        )
        self.approval = request_approval(
            workspace=self.workspace, actor=self.actor, preflight=preflight,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

    def test_command_status_requires_authentication_and_workspace_scope(self):
        url = reverse('command-status', args=[self.command.public_id])
        self.assertEqual(self.client.get(url).status_code, 401)
        self.client.force_login(self.actor)
        self.assertEqual(self.client.get(url).status_code, 404)
        response = self.client.get(url, HTTP_X_WORKSPACE_ID=str(self.workspace.public_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['command']['status'], 'queued')

    def test_other_actor_cannot_enumerate_status(self):
        self.client.force_login(self.other)
        headers = {'HTTP_X_WORKSPACE_ID': str(self.workspace.public_id)}
        command_url = reverse('command-status', args=[self.command.public_id])
        approval_url = reverse('approval-status', args=[self.approval.public_id])
        self.assertEqual(self.client.get(command_url, **headers).status_code, 404)
        self.assertEqual(self.client.get(approval_url, **headers).status_code, 404)

    def test_authorized_reviewer_decision_is_one_time(self):
        self.client.force_login(self.reviewer)
        url = reverse('approval-decision', args=[self.approval.public_id])
        headers = {'HTTP_X_WORKSPACE_ID': str(self.workspace.public_id)}
        response = self.client.post(
            url,
            data={'decision': 'approve', 'reason': 'Exact payload reviewed'},
            content_type='application/json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'approved')
        replay = self.client.post(
            url,
            data={'decision': 'approve'},
            content_type='application/json',
            **headers,
        )
        self.assertEqual(replay.status_code, 409)
