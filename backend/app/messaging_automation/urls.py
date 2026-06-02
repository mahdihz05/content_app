from django.urls import path

from messaging_automation.views.channel_management import (
    RequestChannelVerificationAPIView,
    ConfirmChannelAPIView,
    UserChannelsAPIView,
    PublishToChannelsAPIView,
)
from messaging_automation.views.publish_logs import PublishLogsAPIView
from messaging_automation.views.publish_to_telegram import PublishToTelegramAPIView

urlpatterns = [

    # احراز هویت کانال
    path(
        "api/v1/telegram/request-channel-verification/",
        RequestChannelVerificationAPIView.as_view(),
        name="telegram-request-verification"
    ),
    path(
        "api/v1/telegram/confirm-channel/",
        ConfirmChannelAPIView.as_view(),
        name="telegram-confirm-channel"
    ),

    # مدیریت کانال‌ها
    path(
        "api/v1/telegram/channels/",
        UserChannelsAPIView.as_view(),
        name="telegram-channels"
    ),
    path(
        "api/v1/telegram/channels/<int:channel_id>/",
        UserChannelsAPIView.as_view(),
        name="telegram-channel-detail"
    ),

    # انتشار
    path(
        "api/v1/telegram/publish/",
        PublishToChannelsAPIView.as_view(),
        name="telegram-publish"
    ),
    path(
        "api/v1/telegram/publish-single/",
        PublishToTelegramAPIView.as_view(),
        name="telegram-publish-single"
    ),
    path(
        "api/v1/telegram/logs/<int:content_id>/",
        PublishLogsAPIView.as_view(),
        name="telegram-publish-logs"
    ),
]