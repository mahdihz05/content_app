from django.db import models
from campaigns.models.Campaign import Campaign

class ContentItem(models.Model):
    STATUS_CHOICES = [
        ("idle", "Idle"),
        ("researching", "Researching"),
        ("research_done", "Research Done"),
        ("outlining", "Outlining"),
        ("outline_done", "Outline Done"),
        ("generating", "Generating"),
        ("completed", "Completed"),
    ]
    step = models.CharField(
        max_length=50,
        default="research"
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE,
                                 null=True, blank=True)


    title = models.CharField(max_length=200, default='untitled')

    main_keyword = models.CharField(max_length=100, blank=True)  # ✅ blank=True اضافه شد
    additional_keywords = models.JSONField(default=list)

    description = models.TextField(blank=True)
    goal = models.CharField(max_length=200, null=True, blank=True)

    platform = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=20, default="fa")
    information = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)  # ✅ اضافه شد برای ذخیره اطلاعات استخراج‌شده
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="idle")
    search_source = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
