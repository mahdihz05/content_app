from django.core.management.base import BaseCommand
from campaigns.models import CampaignGoal


class Command(BaseCommand):
    help = "Seed campaign goals"

    def handle(self, *args, **kwargs):

        goals = [
            {
                "goal": "Brand Awareness",
                "short_description": "افزایش آگاهی از برند",
                "description": "هدف کمپین افزایش دیده شدن برند و معرفی آن به مخاطبان جدید است."
            },
            {
                "goal": "Traffic",
                "short_description": "افزایش ترافیک وب‌سایت",
                "description": "هدف کمپین هدایت کاربران به وب‌سایت یا صفحه فرود است."
            },
            {
                "goal": "Lead Generation",
                "short_description": "جمع‌آوری سرنخ فروش",
                "description": "هدف کمپین دریافت اطلاعات تماس کاربران برای پیگیری فروش است."
            },
            {
                "goal": "Engagement",
                "short_description": "افزایش تعامل",
                "description": "هدف کمپین افزایش لایک، کامنت، اشتراک‌گذاری و تعامل کاربران است."
            },
            {
                "goal": "Sales",
                "short_description": "افزایش فروش",
                "description": "هدف کمپین افزایش خرید و تبدیل کاربران به مشتری است."
            },
            {
                "goal": "Content Promotion",
                "short_description": "ترویج محتوا",
                "description": "هدف کمپین افزایش بازدید و انتشار محتوا است."
            },
            {
                "goal": "App Install",
                "short_description": "نصب اپلیکیشن",
                "description": "هدف کمپین افزایش نصب اپلیکیشن موبایل است."
            },
        ]

        for g in goals:
            CampaignGoal.objects.update_or_create(
                goal=g["goal"],
                defaults={
                    "short_description": g["short_description"],
                    "description": g["description"],
                }
            )

        self.stdout.write(self.style.SUCCESS("Campaign goals seeded successfully"))
