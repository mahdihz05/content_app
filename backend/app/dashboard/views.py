# dashboard/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from platforms.models import Platform


# --- Dashboard اصلی ---
@login_required
def dashboard(request):
    """داشبورد اصلی سیستم"""
    return render(request, 'dashboard/dashboard.html')


@login_required
def test(request):
    """صفحه تست"""
    return render(request, 'dashboard/test.html')


# --- کمپین‌های محتوا ---
@login_required
def campaign_list_page(request):
    """صفحه لیست کمپین‌های محتوا"""
    return render(request, "dashboard/campaign_list.html")


@login_required
def create_campaign_page(request):
    """صفحه ایجاد کمپین محتوا"""
    return render(request, "dashboard/create_campaign.html")


@login_required
def campaign_content_items(request, campaign_id):
    """صفحه آیتم‌های محتوای کمپین"""
    return render(request, 'dashboard/campaign_content_items.html', {
        'campaign_id': campaign_id
    })


# --- محتوا ---
@login_required
def content_list_page(request):
    """صفحه لیست محتواها"""
    return render(request, 'dashboard/content_list.html')


@login_required
def create_content_page(request):
    """صفحه ایجاد محتوا با AI"""
    platforms = Platform.objects.all().values("id", "name")
    return render(request, "dashboard/create_content_ai.html", {
        "platforms": list(platforms)
    })


@login_required
def create_content_chat(request):
    """صفحه چت با AI برای تولید محتوا"""
    return render(request, "dashboard/create_content_ai.html")


# --- اتوماسیون پیام‌رسانی ---

@login_required
def messaging_dashboard(request):
    """داشبورد اصلی اتوماسیون پیام‌رسانی"""
    return render(request, 'messaging/dashboard.html')


@login_required
def messaging_accounts_page(request):
    """صفحه مدیریت اکانت‌های متصل"""
    return render(request, 'messaging/accounts.html')


@login_required
def messaging_bulk_send_page(request):
    """صفحه ارسال انبوه پیام"""
    return render(request, 'messaging/bulk_send.html')


@login_required
def messaging_auto_reply_page(request):
    """صفحه پاسخگویی هوشمند خودکار"""
    return render(request, 'messaging/auto_reply.html')


# --- View‌های قدیمی (در صورت نیاز به حفظ سازگاری) ---

@login_required
def account_list_page(request):
    """صفحه لیست اکانت‌ها (redirect به صفحه جدید)"""
    return render(request, 'messaging/accounts.html')


@login_required
def account_create_page(request):
    """صفحه اضافه کردن اکانت (بخشی از accounts.html)"""
    return render(request, 'messaging/accounts.html')


@login_required
def messaging_campaign_list_page(request):
    """صفحه لیست کمپین‌های پیام‌رسانی (بخشی از bulk_send.html)"""
    return render(request, 'messaging/bulk_send.html')

@login_required
def messaging_campaign_create_page(request):
    """صفحه ایجاد کمپین پیام‌رسانی (بخشی از bulk_send.html)"""
    return render(request, 'messaging/bulk_send.html')


@login_required
def messaging_campaign_detail_page(request, pk):
    """صفحه جزئیات کمپین"""
    return render(request, 'messaging/bulk_send.html', {
        'campaign_id': pk
    })


@login_required
def ai_chat_page(request):
    """صفحه چت با AI (بخشی از auto_reply.html)"""
    return render(request, 'messaging/auto_reply.html')


@login_required
def telegram_channels_page(request):
    return render(request, "messaging_automation/telegram_channels.html")
