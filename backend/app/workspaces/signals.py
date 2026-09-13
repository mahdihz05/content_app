import uuid

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Workspace, WorkspaceMembership


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='workspaces.create_personal_workspace')
def create_personal_workspace(sender, instance, created, raw=False, **kwargs):
    if not created or raw:
        return
    suffix = uuid.uuid4().hex[:10]
    name = instance.name or 'Personal workspace'
    with transaction.atomic():
        workspace = Workspace.objects.create(
            name=name,
            slug=f'{slugify(name) or "workspace"}-{suffix}',
            created_by=instance,
        )
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=instance,
            role=WorkspaceMembership.Role.OWNER,
            is_default=True,
        )


def _default_workspace_id(user_id):
    if not user_id:
        return None
    membership = WorkspaceMembership.objects.filter(
        user_id=user_id,
        is_active=True,
    ).order_by('-is_default', 'pk').first()
    return membership.workspace_id if membership else None


def _set_workspace(instance, *candidate_ids):
    candidates = {candidate for candidate in candidate_ids if candidate}
    if instance.workspace_id:
        candidates.add(instance.workspace_id)
    if len(candidates) > 1:
        raise ValidationError('Related records must belong to the same workspace.')
    if not instance.workspace_id and candidates:
        instance.workspace_id = candidates.pop()


@receiver(pre_save, sender='campaigns.Campaign', dispatch_uid='workspaces.map_campaign')
def map_campaign(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(instance, _default_workspace_id(instance.user_id))


@receiver(pre_save, sender='content.ContentItem', dispatch_uid='workspaces.map_content_item')
def map_content_item(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(instance, getattr(instance.campaign, 'workspace_id', None) if instance.campaign_id else None)


@receiver(pre_save, sender='content.AIChatSession', dispatch_uid='workspaces.map_chat_session')
def map_chat_session(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(
            instance,
            _default_workspace_id(instance.user_id),
            getattr(instance.campaign, 'workspace_id', None) if instance.campaign_id else None,
            getattr(instance.content_item, 'workspace_id', None) if instance.content_item_id else None,
        )


@receiver(pre_save, sender='ai.AIJob', dispatch_uid='workspaces.map_ai_job')
def map_ai_job(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(
            instance,
            _default_workspace_id(instance.user_id),
            getattr(instance.content_item, 'workspace_id', None) if instance.content_item_id else None,
        )


@receiver(pre_save, sender='ai.AIInterviewSession', dispatch_uid='workspaces.map_ai_interview')
def map_ai_interview(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(
            instance,
            _default_workspace_id(instance.user_id),
            getattr(instance.content_item, 'workspace_id', None) if instance.content_item_id else None,
            getattr(instance.job, 'workspace_id', None) if instance.job_id else None,
        )


@receiver(pre_save, sender='research.ResearchSource', dispatch_uid='workspaces.map_research_source')
@receiver(pre_save, sender='research.ResearchJob', dispatch_uid='workspaces.map_research_job')
def map_research_record(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(instance, getattr(instance.content_item, 'workspace_id', None))


@receiver(pre_save, sender='platforms.SocialAccount', dispatch_uid='workspaces.map_social_account')
def map_social_account(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(instance, _default_workspace_id(instance.user_id_id))


@receiver(pre_save, sender='messaging_automation.TelegramChannel', dispatch_uid='workspaces.map_telegram_channel')
def map_telegram_channel(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(
            instance,
            _default_workspace_id(instance.user_id),
            getattr(instance.campaign, 'workspace_id', None) if instance.campaign_id else None,
        )


@receiver(pre_save, sender='messaging_automation.ChannelVerification', dispatch_uid='workspaces.map_channel_verification')
def map_channel_verification(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(instance, _default_workspace_id(instance.user_id))


@receiver(pre_save, sender='messaging_automation.TelegramPublishLog', dispatch_uid='workspaces.map_publish_log')
def map_publish_log(sender, instance, raw=False, **kwargs):
    if not raw:
        _set_workspace(
            instance,
            getattr(instance.content_item, 'workspace_id', None),
            getattr(instance.channel, 'workspace_id', None),
        )
