from django.test import TestCase

from automation.policy import workspace_policy_preflight
from automation.registry import ToolRegistry, ToolSpec
from user.models import CustomUser


class WorkspacePolicyPreflightTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user('09120000081', 'password')
        self.workspace = self.owner.workspace_memberships.get(is_default=True).workspace

    def test_workspace_policy_allows_owner_and_requires_consequential_approval(self):
        registry = ToolRegistry()
        registry.register(ToolSpec(
            'content.publish', '1', 'consequential', 'content.publish', '1',
            {'type': 'object'}, {'type': 'object'},
        ))
        preflight = registry.preflight(
            name='content.publish', version='1', payload={}, actor=self.owner,
            workspace=self.workspace, policy_evaluator=workspace_policy_preflight,
        )
        self.assertTrue(preflight.policy.allowed)
        self.assertTrue(preflight.policy.requires_approval)
        self.assertEqual(preflight.policy.policy_version, 'workspace-policy-v1')

    def test_unknown_action_and_non_member_fail_closed(self):
        registry = ToolRegistry()
        registry.register(ToolSpec('unknown.action', '1', 'read', 'unknown', '1', {'type': 'object'}, {'type': 'object'}))
        outsider = CustomUser.objects.create_user('09120000082', 'password')
        for actor in (self.owner, outsider):
            with self.subTest(actor=actor.pk):
                preflight = workspace_policy_preflight(
                    actor=actor,
                    workspace=self.workspace,
                    tool=registry.get('unknown.action', '1'),
                    payload={},
                )
                self.assertFalse(preflight.allowed)
