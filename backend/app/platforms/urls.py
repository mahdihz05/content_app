from django.urls import path
from platforms.views import get_platforms

urlpatterns = [
    path('api/v1/get_platforms', get_platforms, name='get_platforms-api-v1'),


]