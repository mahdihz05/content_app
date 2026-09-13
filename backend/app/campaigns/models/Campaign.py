import uuid

from django.db import models
from django.conf import settings
from campaigns.models.CampaignGoal import CampaignGoal

class Campaign(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='legacy_campaigns',
    )
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    TAG_CHOICES = [
        ('seo', 'SEO'),
        ('blog', 'Blog'),
        ('product', 'Product'),
        ('social', 'Social'),
        ('education', 'Education'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    main_keyword = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    goal = models.ForeignKey(CampaignGoal, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    tag = models.CharField(max_length=50, choices=TAG_CHOICES, default="product")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


