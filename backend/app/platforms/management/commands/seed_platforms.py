from django.core.management.base import BaseCommand
from platforms.models import Platform


class Command(BaseCommand):
    help = "Seed platforms"

    def handle(self, *args, **kwargs):

        platforms = [
            {
                "name": "Instagram",
                "content_type": "social",
                "connection": "api",
                "is_open": True
            },
            {
                "name": "YouTube",
                "content_type": "video",
                "connection": "api",
                "is_open": True
            },
            {
                "name": "TikTok",
                "content_type": "short_video",
                "connection": "api",
                "is_open": True
            },
            {
                "name": "Twitter",
                "content_type": "social",
                "connection": "api",
                "is_open": True
            },
            {
                "name": "LinkedIn",
                "content_type": "professional",
                "connection": "api",
                "is_open": True
            }
        ]

        for p in platforms:
            Platform.objects.update_or_create(
                name=p["name"],
                defaults={
                    "content_type": p["content_type"],
                    "connection": p["connection"],
                    "is_open": p["is_open"],
                }
            )

        self.stdout.write(self.style.SUCCESS("Platforms seeded successfully"))
