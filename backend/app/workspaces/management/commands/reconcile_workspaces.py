import json

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


MODEL_LABELS = (
    'campaigns.Campaign',
    'content.ContentItem',
    'content.AIChatSession',
    'ai.AIJob',
    'ai.AIInterviewSession',
    'research.ResearchSource',
    'research.ResearchJob',
    'platforms.SocialAccount',
    'messaging_automation.TelegramChannel',
    'messaging_automation.ChannelVerification',
    'messaging_automation.TelegramPublishLog',
)


class Command(BaseCommand):
    help = 'Report and optionally repair inferable Phase 1 legacy workspace mappings.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--check', action='store_true')
        parser.add_argument('--json', action='store_true')

    def handle(self, *args, **options):
        report = {}
        unresolved = 0
        for label in MODEL_LABELS:
            model = apps.get_model(label)
            conflicts = 0
            if options['apply']:
                for record in model.objects.filter(workspace__isnull=True).iterator(chunk_size=500):
                    try:
                        record.save(update_fields=('workspace',))
                    except ValidationError:
                        conflicts += 1
            total = model.objects.count()
            unmapped = model.objects.filter(workspace__isnull=True).count()
            missing_public_ids = model.objects.filter(public_id__isnull=True).count()
            report[label] = {
                'total': total,
                'mapped': total - unmapped,
                'unmapped': unmapped,
                'missing_public_ids': missing_public_ids,
                'conflicts': conflicts,
            }
            unresolved += unmapped + missing_public_ids + conflicts

        if options['json']:
            self.stdout.write(json.dumps(report, sort_keys=True))
        else:
            for label, counts in report.items():
                self.stdout.write(
                    f'{label}: total={counts["total"]} mapped={counts["mapped"]} '
                    f'unmapped={counts["unmapped"]} public_id_missing={counts["missing_public_ids"]} '
                    f'conflicts={counts["conflicts"]}'
                )
        if options['check'] and unresolved:
            raise CommandError(f'Workspace reconciliation found {unresolved} unresolved mapping issue(s).')
