# dashboard/urls.py

from django.urls import path

from .views import (

    # =========================================
    # MAIN DASHBOARD
    # =========================================

    dashboard,
    test,

    # =========================================
    # CONTENT CAMPAIGNS
    # =========================================

    campaign_list_page,
    create_campaign_page,
    campaign_content_items,

    # =========================================
    # CONTENT
    # =========================================

    create_content_page,
    content_list_page,
    create_content_chat,

    # =========================================
    # MESSAGING AUTOMATION PAGES
    # =========================================

    messaging_dashboard,
    messaging_accounts_page,
    messaging_bulk_send_page,
    messaging_auto_reply_page,

    # =========================================
    # OLD COMPATIBILITY VIEWS
    # =========================================

    account_list_page,
    account_create_page,

    messaging_campaign_list_page,
    messaging_campaign_create_page,
    messaging_campaign_detail_page,

    ai_chat_page,
)

urlpatterns = [

    # =====================================================
    # MAIN DASHBOARD
    # =====================================================

    path(
        '',
        dashboard,
        name='dashboard'
    ),

    path(
        'test/',
        test,
        name='test'
    ),

    # =====================================================
    # CONTENT CAMPAIGNS
    # =====================================================

    path(
        'campaign-list/',
        campaign_list_page,
        name='campaign-list-page'
    ),

    path(
        'create-campaign/',
        create_campaign_page,
        name='create-campaign-page'
    ),

    path(
        'campaign/content-items/<int:campaign_id>/',
        campaign_content_items,
        name='campaign-content-items-page'
    ),

    # =====================================================
    # CONTENT
    # =====================================================

    path(
        'content/create/',
        create_content_page,
        name='create-content-page'
    ),

    path(
        'content/list/',
        content_list_page,
        name='content-list-page'
    ),

    path(
        'content/chat/',
        create_content_chat,
        name='create-content-chat-page'
    ),

    # =====================================================
    # NEW MESSAGING PAGES
    # =====================================================

    path(
        'messaging/',
        messaging_dashboard,
        name='messaging-dashboard'
    ),

    path(
        'messaging/accounts/',
        messaging_accounts_page,
        name='messaging-accounts'
    ),

    path(
        'messaging/bulk-send/',
        messaging_bulk_send_page,
        name='messaging-bulk-send'
    ),

    path(
        'messaging/auto-reply/',
        messaging_auto_reply_page,
        name='messaging-auto-reply'
    ),

    # =====================================================
    # OLD URLS (KEEP FOR COMPATIBILITY)
    # =====================================================

    path(
        'messaging/accounts/list/',
        account_list_page,
        name='messaging-account-list-page'
    ),

    path(
        'messaging/accounts/create/',
        account_create_page,
        name='messaging-account-create-page'
    ),

    path(
        'messaging/campaigns/',
        messaging_campaign_list_page,
        name='messaging-campaign-list-page'
    ),

    path(
        'messaging/campaigns/create/',
        messaging_campaign_create_page,
        name='messaging-campaign-create-page'
    ),

    path(
        'messaging/campaigns/<int:pk>/',
        messaging_campaign_detail_page,
        name='messaging-campaign-detail-page'
    ),

    path(
        'messaging/ai-chat/',
        ai_chat_page,
        name='messaging-ai-chat-page'
    ),
]