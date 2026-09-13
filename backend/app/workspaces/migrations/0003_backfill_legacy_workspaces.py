import uuid

from django.db import migrations


def _workspace_id(*values):
    candidates = {value for value in values if value}
    return candidates.pop() if len(candidates) == 1 else None


def _backfill(model, queryset, resolver):
    pending = []
    for record in queryset.iterator(chunk_size=500):
        record.public_id = record.public_id or uuid.uuid4()
        record.workspace_id = record.workspace_id or resolver(record)
        pending.append(record)
        if len(pending) == 500:
            model.objects.bulk_update(pending, ('public_id', 'workspace'))
            pending = []
    if pending:
        model.objects.bulk_update(pending, ('public_id', 'workspace'))


def backfill_legacy_workspaces(apps, schema_editor):
    Membership = apps.get_model('workspaces', 'WorkspaceMembership')
    default_workspaces = {}
    memberships = Membership.objects.filter(is_active=True).order_by('user_id', '-is_default', 'pk')
    for membership in memberships.iterator():
        default_workspaces.setdefault(membership.user_id, membership.workspace_id)

    Campaign = apps.get_model('campaigns', 'Campaign')
    _backfill(
        Campaign,
        Campaign.objects.all(),
        lambda record: default_workspaces.get(record.user_id),
    )

    ContentItem = apps.get_model('content', 'ContentItem')
    _backfill(
        ContentItem,
        ContentItem.objects.select_related('campaign'),
        lambda record: record.campaign.workspace_id if record.campaign_id else None,
    )

    AIChatSession = apps.get_model('content', 'AIChatSession')
    _backfill(
        AIChatSession,
        AIChatSession.objects.select_related('campaign', 'content_item'),
        lambda record: _workspace_id(
            default_workspaces.get(record.user_id),
            record.campaign.workspace_id if record.campaign_id else None,
            record.content_item.workspace_id if record.content_item_id else None,
        ),
    )

    AIJob = apps.get_model('ai', 'AIJob')
    _backfill(
        AIJob,
        AIJob.objects.select_related('content_item'),
        lambda record: _workspace_id(
            default_workspaces.get(record.user_id),
            record.content_item.workspace_id if record.content_item_id else None,
        ),
    )

    AIInterviewSession = apps.get_model('ai', 'AIInterviewSession')
    _backfill(
        AIInterviewSession,
        AIInterviewSession.objects.select_related('content_item', 'job'),
        lambda record: _workspace_id(
            default_workspaces.get(record.user_id),
            record.content_item.workspace_id if record.content_item_id else None,
            record.job.workspace_id if record.job_id else None,
        ),
    )

    ResearchSource = apps.get_model('research', 'ResearchSource')
    _backfill(
        ResearchSource,
        ResearchSource.objects.select_related('content_item'),
        lambda record: record.content_item.workspace_id,
    )
    ResearchJob = apps.get_model('research', 'ResearchJob')
    _backfill(
        ResearchJob,
        ResearchJob.objects.select_related('content_item'),
        lambda record: record.content_item.workspace_id,
    )

    SocialAccount = apps.get_model('platforms', 'SocialAccount')
    _backfill(
        SocialAccount,
        SocialAccount.objects.all(),
        lambda record: default_workspaces.get(record.user_id_id),
    )

    TelegramChannel = apps.get_model('messaging_automation', 'TelegramChannel')
    _backfill(
        TelegramChannel,
        TelegramChannel.objects.select_related('campaign'),
        lambda record: _workspace_id(
            default_workspaces.get(record.user_id),
            record.campaign.workspace_id if record.campaign_id else None,
        ),
    )
    ChannelVerification = apps.get_model('messaging_automation', 'ChannelVerification')
    _backfill(
        ChannelVerification,
        ChannelVerification.objects.all(),
        lambda record: default_workspaces.get(record.user_id),
    )
    TelegramPublishLog = apps.get_model('messaging_automation', 'TelegramPublishLog')
    _backfill(
        TelegramPublishLog,
        TelegramPublishLog.objects.select_related('content_item', 'channel'),
        lambda record: _workspace_id(
            record.content_item.workspace_id,
            record.channel.workspace_id,
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('workspaces', '0002_backfill_personal_workspaces'),
        ('campaigns', '0010_campaign_public_id_campaign_workspace'),
        ('content', '0020_aichatsession_public_id_aichatsession_workspace_and_more'),
        ('ai', '0003_aiinterviewsession_public_id_and_more'),
        ('research', '0003_researchjob_public_id_researchjob_workspace_and_more'),
        ('platforms', '0003_socialaccount_public_id_socialaccount_workspace'),
        ('messaging_automation', '0003_channelverification_public_id_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_legacy_workspaces, migrations.RunPython.noop),
    ]
