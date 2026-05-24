from django.core.management.base import BaseCommand
from campaigns.models import CampaignFormSchema, CampaignGoal


class Command(BaseCommand):
    help = "Seed campaign form schemas"

    def handle(self, *args, **kwargs):

        brand_awareness, _ = CampaignGoal.objects.get_or_create(goal="Brand Awareness")
        traffic, _ = CampaignGoal.objects.get_or_create(goal="Traffic")
        leads, _ = CampaignGoal.objects.get_or_create(goal="Lead Generation")
        sales, _ = CampaignGoal.objects.get_or_create(goal="Sales")

        base_campaign_fields = [
            {"name": "title", "type": "text", "label": "عنوان کمپین", "required": True},
            {"name": "main_keyword", "type": "text", "label": "کلمه کلیدی اصلی", "required": True},
            {"name": "description", "type": "textarea", "label": "توضیحات کمپین", "required": False},
            {
                "name": "tag",
                "type": "select",
                "label": "نوع محتوا",
                "options": ["seo", "blog", "product", "social", "education"],
                "required": True
            }
        ]

        schemas = [

            {
                "goal": brand_awareness,
                "schema_json": {
                    "fields": base_campaign_fields + [
                        {"name": "brand_message", "type": "textarea", "label": "پیام برند", "required": True},
                        {"name": "target_audience", "type": "text", "label": "مخاطب هدف", "required": True},
                        {"name": "budget", "type": "number", "label": "بودجه", "required": False},
                    ]
                }
            },

            {
                "goal": traffic,
                "schema_json": {
                    "fields": base_campaign_fields + [
                        {"name": "target_url", "type": "url", "label": "لینک مقصد", "required": False},
                        {
                            "name": "content_strategy",
                            "type": "select",
                            "label": "استراتژی محتوا",
                            "options": ["seo_articles", "social_posts", "mixed"],
                            "required": True
                        },
                        {"name": "budget", "type": "number", "label": "بودجه", "required": False},
                    ]
                }
            },

            {
                "goal": leads,
                "schema_json": {
                    "fields": base_campaign_fields + [
                        {
                            "name": "lead_type",
                            "type": "select",
                            "label": "نوع لید",
                            "options": ["email", "phone", "both"],
                            "required": True
                        },
                        {"name": "offer_description", "type": "textarea", "label": "توضیح پیشنهاد", "required": True},
                        {"name": "budget", "type": "number", "label": "بودجه", "required": False},
                    ]
                }
            },

            {
                "goal": sales,
                "schema_json": {
                    "fields": base_campaign_fields + [
                        {"name": "product_name", "type": "text", "label": "نام محصول", "required": True},
                        {"name": "product_url", "type": "url", "label": "لینک محصول", "required": True},
                        {"name": "price_range", "type": "text", "label": "بازه قیمت", "required": False},
                        {"name": "budget", "type": "number", "label": "بودجه", "required": False},
                    ]
                }
            },
        ]

        created = 0

        for schema in schemas:
            obj, was_created = CampaignFormSchema.objects.update_or_create(
                goal=schema["goal"],
                version=1,
                defaults={
                    "schema_json": schema["schema_json"],
                    "is_active": True
                }
            )

            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created} form schemas created/updated successfully")
        )
