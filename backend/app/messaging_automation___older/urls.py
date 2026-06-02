# messaging_automation/urls.py

from django.urls import path

from messaging_automation.views.dashboard_views import (
    DashboardStatsAPIView
)

from messaging_automation.views.account_views import (
    AccountListAPIView,
    AccountCreateAPIView,
)

from messaging_automation.views.campaign_views import (
    CampaignListAPIView,
    CampaignCreateAPIView,
    CampaignDetailAPIView,
)

from messaging_automation.views.ai_views import (
    AIChatAPIView
)

from messaging_automation.views.bulk_send_views import (
    BulkSendCreateAPIView
)


from django.http import JsonResponse

def bulk_send_list_api(request):

    return JsonResponse([], safe=False)


def auto_reply_list_api(request):

    return JsonResponse([], safe=False)

urlpatterns = [

    path(
        "api/bulk-send/",
        bulk_send_list_api,
        name="messaging-api-bulk-send-list"
    ),

    path(
        "api/bulk-send/create/",
        BulkSendCreateAPIView.as_view(),
        name="messaging-api-bulk-send-create"
    ),

    path(
        "api/auto-reply/",
        auto_reply_list_api,
        name="messaging-api-auto-reply-list"
    ),

    # =====================================================
    # DASHBOARD API
    # =====================================================

    path(
        "dashboard/stats/",
        DashboardStatsAPIView.as_view(),
        name="messaging-api-dashboard-stats"
    ),

    # =====================================================
    # ACCOUNT API
    # =====================================================

    path(
        "api/accounts/",
        AccountListAPIView.as_view(),
        name="messaging-api-account-list"
    ),

    path(
        "api/accounts/create/",
        AccountCreateAPIView.as_view(),
        name="messaging-api-account-create"
    ),

    # =====================================================
    # CAMPAIGN API
    # =====================================================

    path(
        "campaigns/",
        CampaignListAPIView.as_view(),
        name="messaging-api-campaign-list"
    ),

    path(
        "campaigns/create/",
        CampaignCreateAPIView.as_view(),
        name="messaging-api-campaign-create"
    ),

    path(
        "campaigns/<int:campaign_id>/",
        CampaignDetailAPIView.as_view(),
        name="messaging-api-campaign-detail"
    ),

    # =====================================================
    # AI CHAT API
    # =====================================================

    path(
        "ai/chat/",
        AIChatAPIView.as_view(),
        name="messaging-api-ai-chat"
    ),
]