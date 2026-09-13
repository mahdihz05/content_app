from django.urls import path

from .views import (
    CurrentWorkspaceView,
    MyMembershipListView,
    SwitchWorkspaceView,
    WorkspaceMemberDetailView,
    WorkspaceMemberListView,
)


app_name = 'workspaces'

urlpatterns = [
    path('workspace/', CurrentWorkspaceView.as_view(), name='current'),
    path('workspace/switch/', SwitchWorkspaceView.as_view(), name='switch'),
    path('workspaces/', MyMembershipListView.as_view(), name='membership-list'),
    path('workspace/members/', WorkspaceMemberListView.as_view(), name='member-list'),
    path(
        'workspace/members/<int:membership_id>/',
        WorkspaceMemberDetailView.as_view(),
        name='member-detail',
    ),
]
