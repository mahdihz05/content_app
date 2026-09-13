from django.urls import path

from automation.views import (
    ApprovalDecisionView,
    ApprovalStatusView,
    CommandStatusView,
    ExecutionCallbackView,
)


app_name = 'automation'

urlpatterns = [
    path('commands/<uuid:public_id>/', CommandStatusView.as_view(), name='command-status'),
    path('approvals/<uuid:public_id>/', ApprovalStatusView.as_view(), name='approval-status'),
    path('approvals/<uuid:public_id>/decision/', ApprovalDecisionView.as_view(), name='approval-decision'),
    path('callbacks/executions/', ExecutionCallbackView.as_view(), name='execution-callback'),
]
