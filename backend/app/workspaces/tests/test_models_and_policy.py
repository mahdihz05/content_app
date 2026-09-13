from django.db import IntegrityError, transaction

from workspaces.models import PolicyGrant, WorkspaceMembership
from workspaces.policy import ACTION_EFFECTS, ACTION_ROLES, evaluate_policy

from .base import WorkspaceTestCase


class MembershipConstraintTests(WorkspaceTestCase):
    def test_user_can_have_only_one_membership_per_workspace(self):
        user, membership = self.create_user()
        with self.assertRaises(IntegrityError), transaction.atomic():
            WorkspaceMembership.objects.create(
                workspace=membership.workspace,
                user=user,
                role=WorkspaceMembership.Role.VIEWER,
            )

    def test_default_membership_must_be_active(self):
        user, membership = self.create_user()
        membership.is_active = False
        with self.assertRaises(IntegrityError), transaction.atomic():
            membership.save()

    def test_user_can_have_only_one_default_membership(self):
        user, first = self.create_user()
        other_user, other = self.create_user()
        with self.assertRaises(IntegrityError), transaction.atomic():
            WorkspaceMembership.objects.create(
                workspace=other.workspace,
                user=user,
                role=WorkspaceMembership.Role.VIEWER,
                is_default=True,
            )


class RoleMatrixTests(WorkspaceTestCase):
    def setUp(self):
        self.user, self.membership = self.create_user()

    def test_every_role_action_combination_matches_the_declared_matrix(self):
        for role in WorkspaceMembership.Role.values:
            self.membership.role = role
            for action, effect_class in ACTION_EFFECTS.items():
                with self.subTest(role=role, action=action):
                    expected = effect_class in {
                        WorkspaceMembership.Role.OWNER: PolicyGrant.EffectClass.values,
                        WorkspaceMembership.Role.ADMIN: PolicyGrant.EffectClass.values,
                        WorkspaceMembership.Role.EDITOR: {
                            PolicyGrant.EffectClass.READ,
                            PolicyGrant.EffectClass.DRAFT,
                            PolicyGrant.EffectClass.MUTATE_INTERNAL,
                        },
                        WorkspaceMembership.Role.CONTRIBUTOR: {
                            PolicyGrant.EffectClass.READ,
                            PolicyGrant.EffectClass.DRAFT,
                        },
                        WorkspaceMembership.Role.ANALYST: {PolicyGrant.EffectClass.READ},
                        WorkspaceMembership.Role.VIEWER: {PolicyGrant.EffectClass.READ},
                    }[role]
                    if action in ACTION_ROLES:
                        expected = expected and role in ACTION_ROLES[action]
                    self.assertEqual(evaluate_policy(self.membership, action).allowed, expected)

    def test_inactive_membership_is_always_denied(self):
        self.membership.is_active = False
        for action in ACTION_EFFECTS:
            with self.subTest(action=action):
                self.assertFalse(evaluate_policy(self.membership, action).allowed)

    def test_persisted_grant_can_allow_or_deny_a_role_default(self):
        grant = PolicyGrant.objects.create(
            workspace=self.membership.workspace,
            role=WorkspaceMembership.Role.OWNER,
            action='content.view',
            effect_class=PolicyGrant.EffectClass.READ,
            is_allowed=False,
            created_by=self.user,
        )
        self.assertFalse(evaluate_policy(self.membership, 'content.view').allowed)
        grant.is_allowed = True
        grant.save()
        self.assertTrue(evaluate_policy(self.membership, 'content.view').allowed)

    def test_grant_with_wrong_effect_class_fails_closed(self):
        PolicyGrant.objects.create(
            workspace=self.membership.workspace,
            role=WorkspaceMembership.Role.OWNER,
            action='content.view',
            effect_class=PolicyGrant.EffectClass.CONSEQUENTIAL,
            is_allowed=True,
            created_by=self.user,
        )
        decision = evaluate_policy(self.membership, 'content.view')
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.source, 'invalid_policy_grant')

    def test_grant_cannot_elevate_viewer_to_membership_administration(self):
        self.membership.role = WorkspaceMembership.Role.VIEWER
        PolicyGrant.objects.create(
            workspace=self.membership.workspace,
            role=WorkspaceMembership.Role.VIEWER,
            action='membership.manage',
            effect_class=PolicyGrant.EffectClass.MUTATE_INTERNAL,
            is_allowed=True,
            created_by=self.user,
        )
        decision = evaluate_policy(self.membership, 'membership.manage')
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.source, 'restricted_action')
