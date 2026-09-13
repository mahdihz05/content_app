from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from user.views import register_view, login_view, get_user, get_users, home
from dashboard.views import test
from ai.views.landing_view import landing_chat_api, landing_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v2/', include('common.urls')),
    path('api/v2/', include('workspaces.urls')),
    path('api/v2/internal/', include('automation.urls')),

    # Apps
    path('auth/', include('user.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('campaign/', include('campaigns.urls')),
    path('platform/', include('platforms.urls')),
    path('content/', include('content.urls')),
    path('research/', include('research.urls')),
    path('messaging/', include('messaging_automation.urls')),
    # path('bale/', include('bale_bot.urls')),  # اضافه شد

    # Landing & Test
    path('', landing_view, name='landing'),
    path('api/chat/', landing_chat_api, name='landing_chat_api'),
    path('test/', test, name='test'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
