from automation.registry import PolicyDecision
from workspaces.models import PolicyGrant, WorkspaceMembership
from workspaces.policy import evaluate_policy


POLICY_ADAPTER_VERSION = 'workspace-policy-v1'
EFFECT_COMPATIBILITY = {
    'read': {'read'},
    'draft': {'draft'},
    'mutate_internal': {'mutate_internal'},
    'consequential': {'consequential'},
}


def workspace_policy_preflight(*, actor, workspace, tool, payload):
    """Adapt the workspace role policy to the fail-closed tool policy contract."""
    del payload
    membership = WorkspaceMembership.objects.filter(
        workspace=workspace,
        user=actor,
        is_active=True,
    ).first()
    if membership is None:
        return PolicyDecision(False, tool.effect == 'consequential', POLICY_ADAPTER_VERSION, 'No active workspace membership.')
    try:
        decision = evaluate_policy(membership, tool.name)
    except ValueError:
        return PolicyDecision(False, tool.effect == 'consequential', POLICY_ADAPTER_VERSION, 'Tool has no workspace policy action.')
    effect_matches = decision.effect_class in EFFECT_COMPATIBILITY[tool.effect]
    grant = PolicyGrant.objects.filter(
        workspace=workspace,
        role=membership.role,
        action=tool.name,
    ).first()
    facts = {
        'action': decision.action,
        'effect_class': decision.effect_class,
        'membership_id': membership.pk,
        'role': membership.role,
        'source': decision.source,
        'grant_updated_at': grant.updated_at.isoformat() if grant else None,
    }
    return PolicyDecision(
        allowed=decision.allowed and effect_matches,
        requires_approval=tool.effect == 'consequential',
        policy_version=POLICY_ADAPTER_VERSION,
        reason='' if effect_matches else 'Tool and workspace policy effects do not match.',
        facts=facts,
    )
