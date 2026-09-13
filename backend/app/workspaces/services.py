from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import WorkspaceMembership


ADMIN_ROLES = {
    WorkspaceMembership.Role.OWNER,
    WorkspaceMembership.Role.ADMIN,
}


def _validate_actor(actor_membership, target=None, new_role=None):
    if not actor_membership.is_active or actor_membership.role not in ADMIN_ROLES:
        raise ValidationError('An active owner or admin membership is required.')
    if actor_membership.role == WorkspaceMembership.Role.ADMIN:
        if target is not None and target.role == WorkspaceMembership.Role.OWNER:
            raise ValidationError('Admins cannot modify owners.')
        if new_role == WorkspaceMembership.Role.OWNER:
            raise ValidationError('Admins cannot assign the owner role.')


def create_membership(actor_membership, user, role, *, is_default=False):
    _validate_actor(actor_membership, new_role=role)
    if role not in WorkspaceMembership.Role.values:
        raise ValidationError({'role': 'Unknown workspace role.'})
    try:
        with transaction.atomic():
            if is_default:
                list(
                    WorkspaceMembership.objects.select_for_update()
                    .filter(user=user)
                    .order_by('pk')
                )
                WorkspaceMembership.objects.filter(user=user, is_default=True).update(
                    is_default=False
                )
            return WorkspaceMembership.objects.create(
                workspace=actor_membership.workspace,
                user=user,
                role=role,
                is_active=True,
                is_default=is_default,
            )
    except IntegrityError as exc:
        raise ValidationError('The user already has a membership in this workspace.') from exc


def update_membership(
    actor_membership,
    membership,
    *,
    role=None,
    is_active=None,
    is_default=None,
):
    if membership.workspace_id != actor_membership.workspace_id:
        raise ValidationError('Membership does not belong to the selected workspace.')
    _validate_actor(actor_membership, target=membership, new_role=role)
    if role is not None and role not in WorkspaceMembership.Role.values:
        raise ValidationError({'role': 'Unknown workspace role.'})

    with transaction.atomic():
        locked_memberships = list(
            WorkspaceMembership.objects.select_for_update()
            .filter(workspace=membership.workspace)
            .order_by('pk')
        )
        membership = next(item for item in locked_memberships if item.pk == membership.pk)
        resulting_role = role if role is not None else membership.role
        resulting_active = is_active if is_active is not None else membership.is_active
        if (
            membership.role == WorkspaceMembership.Role.OWNER
            and membership.is_active
            and (resulting_role != WorkspaceMembership.Role.OWNER or not resulting_active)
            and not any(
                item.pk != membership.pk
                and item.role == WorkspaceMembership.Role.OWNER
                and item.is_active
                for item in locked_memberships
            )
        ):
            raise ValidationError('The last active owner cannot be removed or demoted.')

        if role is not None:
            membership.role = role
        if is_active is not None:
            membership.is_active = is_active
            if not is_active:
                membership.is_default = False
        if is_default is not None:
            if is_default and not membership.is_active:
                raise ValidationError({'is_default': 'An inactive membership cannot be default.'})
            if is_default:
                WorkspaceMembership.objects.filter(
                    user=membership.user,
                    is_default=True,
                ).exclude(pk=membership.pk).update(is_default=False)
            membership.is_default = is_default
        membership.full_clean()
        membership.save()
    return membership


def delete_membership(actor_membership, membership):
    update_membership(actor_membership, membership, is_active=False)
