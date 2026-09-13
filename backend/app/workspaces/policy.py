from dataclasses import dataclass

from rest_framework.exceptions import PermissionDenied

from .models import PolicyGrant, WorkspaceMembership


class Actions:
    WORKSPACE_VIEW = 'workspace.view'
    WORKSPACE_MANAGE = 'workspace.manage'
    MEMBERSHIP_VIEW = 'membership.view'
    MEMBERSHIP_MANAGE = 'membership.manage'
    CONTENT_VIEW = 'content.view'
    CONTENT_DRAFT = 'content.draft'
    CONTENT_MUTATE = 'content.mutate'
    CONTENT_PUBLISH = 'content.publish'
    CONTENT_DELETE = 'content.delete'
    ANALYTICS_VIEW = 'analytics.view'
    CONNECTION_MANAGE = 'connection.manage'


ACTION_EFFECTS = {
    Actions.WORKSPACE_VIEW: PolicyGrant.EffectClass.READ,
    Actions.WORKSPACE_MANAGE: PolicyGrant.EffectClass.MUTATE_INTERNAL,
    Actions.MEMBERSHIP_VIEW: PolicyGrant.EffectClass.READ,
    Actions.MEMBERSHIP_MANAGE: PolicyGrant.EffectClass.MUTATE_INTERNAL,
    Actions.CONTENT_VIEW: PolicyGrant.EffectClass.READ,
    Actions.CONTENT_DRAFT: PolicyGrant.EffectClass.DRAFT,
    Actions.CONTENT_MUTATE: PolicyGrant.EffectClass.MUTATE_INTERNAL,
    Actions.CONTENT_PUBLISH: PolicyGrant.EffectClass.CONSEQUENTIAL,
    Actions.CONTENT_DELETE: PolicyGrant.EffectClass.CONSEQUENTIAL,
    Actions.ANALYTICS_VIEW: PolicyGrant.EffectClass.READ,
    Actions.CONNECTION_MANAGE: PolicyGrant.EffectClass.CONSEQUENTIAL,
}

ROLE_EFFECTS = {
    WorkspaceMembership.Role.OWNER: frozenset(PolicyGrant.EffectClass.values),
    WorkspaceMembership.Role.ADMIN: frozenset(PolicyGrant.EffectClass.values),
    WorkspaceMembership.Role.EDITOR: frozenset({
        PolicyGrant.EffectClass.READ,
        PolicyGrant.EffectClass.DRAFT,
        PolicyGrant.EffectClass.MUTATE_INTERNAL,
    }),
    WorkspaceMembership.Role.CONTRIBUTOR: frozenset({
        PolicyGrant.EffectClass.READ,
        PolicyGrant.EffectClass.DRAFT,
    }),
    WorkspaceMembership.Role.ANALYST: frozenset({PolicyGrant.EffectClass.READ}),
    WorkspaceMembership.Role.VIEWER: frozenset({PolicyGrant.EffectClass.READ}),
}

# Read effects are intentionally narrowed for administrative and analytical data.
ACTION_ROLES = {
    Actions.MEMBERSHIP_VIEW: frozenset({
        WorkspaceMembership.Role.OWNER,
        WorkspaceMembership.Role.ADMIN,
    }),
    Actions.MEMBERSHIP_MANAGE: frozenset({
        WorkspaceMembership.Role.OWNER,
        WorkspaceMembership.Role.ADMIN,
    }),
    Actions.ANALYTICS_VIEW: frozenset({
        WorkspaceMembership.Role.OWNER,
        WorkspaceMembership.Role.ADMIN,
        WorkspaceMembership.Role.EDITOR,
        WorkspaceMembership.Role.ANALYST,
    }),
}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    action: str
    effect_class: str
    source: str


def effect_class_for(action):
    try:
        return ACTION_EFFECTS[action]
    except KeyError:
        raise ValueError(f'Unknown policy action: {action}') from None


def evaluate_policy(membership, action):
    effect_class = effect_class_for(action)
    if not membership.is_active:
        return PolicyDecision(False, action, effect_class, 'inactive_membership')

    allowed_roles = ACTION_ROLES.get(action)
    if allowed_roles is not None and membership.role not in allowed_roles:
        return PolicyDecision(False, action, effect_class, 'restricted_action')

    grant = PolicyGrant.objects.filter(
        workspace=membership.workspace,
        role=membership.role,
        action=action,
    ).first()
    if grant is not None:
        if grant.effect_class != effect_class:
            return PolicyDecision(False, action, effect_class, 'invalid_policy_grant')
        return PolicyDecision(grant.is_allowed, action, effect_class, 'policy_grant')

    allowed = effect_class in ROLE_EFFECTS.get(membership.role, ())
    return PolicyDecision(allowed, action, effect_class, 'role_default')


def require_policy(membership, action):
    decision = evaluate_policy(membership, action)
    if not decision.allowed:
        raise PermissionDenied()
    return decision
