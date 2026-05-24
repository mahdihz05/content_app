from django.core.management.base import BaseCommand
from content.models import ContentFormSchema
from platforms.models import Platform


class Command(BaseCommand):

    help = "Seed content form schemas"

    def handle(self, *args, **kwargs):

        schemas = {

            "Instagram": {
                "fields": [
                    {"name": "caption", "label": "Caption", "type": "textarea", "required": True},
                    {"name": "tone", "label": "Tone", "type": "select", "options": ["casual", "fun", "professional"]},
                    {"name": "hashtags", "label": "Hashtags", "type": "text"},
                    {"name": "cta", "label": "Call To Action", "type": "text"}
                ]
            },

            "YouTube": {
                "fields": [
                    {"name": "title", "label": "Video Title", "type": "text", "required": True},
                    {"name": "description", "label": "Description", "type": "textarea"},
                    {"name": "tags", "label": "Tags", "type": "text"},
                    {"name": "video_length", "label": "Video Length", "type": "select",
                     "options": ["short", "medium", "long"]}
                ]
            },

            "TikTok": {
                "fields": [
                    {"name": "caption", "label": "Caption", "type": "textarea"},
                    {"name": "hook", "label": "Opening Hook", "type": "text"},
                    {"name": "hashtags", "label": "Hashtags", "type": "text"},
                    {"name": "tone", "label": "Tone", "type": "select",
                     "options": ["fun", "energetic", "storytelling"]}
                ]
            },

            "Twitter": {
                "fields": [
                    {"name": "tweet_text", "label": "Tweet Text", "type": "textarea", "required": True},
                    {"name": "tone", "label": "Tone", "type": "select",
                     "options": ["professional", "casual", "funny"]},
                    {"name": "hashtags", "label": "Hashtags", "type": "text"}
                ]
            },

            "LinkedIn": {
                "fields": [
                    {"name": "post_text", "label": "Post Text", "type": "textarea", "required": True},
                    {"name": "tone", "label": "Tone", "type": "select",
                     "options": ["professional", "thought_leadership", "storytelling"]},
                    {"name": "cta", "label": "Call To Action", "type": "text"}
                ]
            },

            "Website": {
                "fields": [
                    {"name": "title", "label": "Page Title", "type": "text", "required": True},
                    {"name": "meta_description", "label": "Meta Description", "type": "textarea"},
                    {"name": "main_keyword", "label": "Main Keyword", "type": "text"},
                    {"name": "content_length", "label": "Content Length", "type": "select",
                     "options": ["short", "medium", "long"]}
                ]
            },

            "Test Platform": {
                "fields": [
                    {"name": "title", "label": "Title", "type": "text"},
                    {"name": "description", "label": "Description", "type": "textarea"}
                ]
            }

        }

        for name, schema in schemas.items():

            try:

                platform = Platform.objects.get(name=name)

                ContentFormSchema.objects.get_or_create(
                    platform=platform,
                    version=1,
                    defaults={
                        "schema": schema,
                        "is_active": True
                    }
                )

                self.stdout.write(self.style.SUCCESS(f"Schema created for {name}"))

            except Platform.DoesNotExist:

                self.stdout.write(self.style.WARNING(f"Platform {name} not found"))
