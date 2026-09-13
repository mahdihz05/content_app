from django.urls import path

from common.views import HealthView, ReadinessView


app_name = 'common'

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('readiness/', ReadinessView.as_view(), name='readiness'),
]
