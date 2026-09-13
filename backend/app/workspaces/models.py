import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Workspace(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_workspaces',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', 'id')

    def __str__(self):
        return self.name


class WorkspaceMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        EDITOR = 'editor', 'Editor'
        CONTRIBUTOR = 'contributor', 'Contributor'
        ANALYST = 'analyst', 'Analyst'
        VIEWER = 'viewer', 'Viewer'

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspace_memberships',
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('workspace_id', 'user_id')
        constraints = [
            models.UniqueConstraint(
                fields=('workspace', 'user'),
                name='workspace_unique_membership',
            ),
            models.CheckConstraint(
                condition=Q(is_default=False) | Q(is_active=True),
                name='workspace_default_membership_active',
            ),
            models.UniqueConstraint(
                fields=('user',),
                condition=Q(is_default=True),
                name='workspace_one_default_per_user',
            ),
        ]

    def clean(self):
        if self.is_default and not self.is_active:
            raise ValidationError({'is_default': 'A default membership must be active.'})

    def __str__(self):
        return f'{self.user_id}:{self.workspace_id}:{self.role}'


class WorkspaceFeatureFlag(models.Model):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='feature_flags',
    )
    name = models.CharField(max_length=120)
    is_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('workspace', 'name'),
                name='workspace_unique_feature_flag',
            ),
        ]


class PolicyGrant(models.Model):
    class EffectClass(models.TextChoices):
        READ = 'read', 'Read'
        DRAFT = 'draft', 'Draft'
        MUTATE_INTERNAL = 'mutate_internal', 'Mutate internal'
        CONSEQUENTIAL = 'consequential', 'Consequential'

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='policy_grants',
    )
    role = models.CharField(max_length=16, choices=WorkspaceMembership.Role.choices)
    action = models.CharField(max_length=120)
    effect_class = models.CharField(max_length=20, choices=EffectClass.choices)
    is_allowed = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='workspace_policy_grants',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('workspace_id', 'role', 'action')
        constraints = [
            models.UniqueConstraint(
                fields=('workspace', 'role', 'action'),
                name='workspace_unique_role_action_grant',
            ),
        ]

    def __str__(self):
        decision = 'allow' if self.is_allowed else 'deny'
        return f'{self.workspace_id}:{self.role}:{self.action}:{decision}'
