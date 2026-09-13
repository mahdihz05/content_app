from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.api import V2APIView, error_payload

from .context import resolve_workspace_context, select_workspace
from .models import WorkspaceMembership
from .policy import Actions, require_policy
from .serializers import (
    MembershipCreateSerializer,
    MembershipSerializer,
    MembershipUpdateSerializer,
    SwitchWorkspaceSerializer,
    WorkspaceSerializer,
)
from .services import create_membership, delete_membership, update_membership


def _validation_error(request, exc):
    details = getattr(exc, 'message_dict', None) or {'non_field_errors': exc.messages}
    return Response(
        error_payload(request, 'invalid_membership', 'Membership change is invalid.', details),
        status=status.HTTP_400_BAD_REQUEST,
    )


class CurrentWorkspaceView(V2APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = resolve_workspace_context(request)
        return Response({
            'workspace': WorkspaceSerializer(context.workspace).data,
            'membership': MembershipSerializer(context.membership).data,
        })


class SwitchWorkspaceView(V2APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwitchWorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = select_workspace(
            request,
            serializer.validated_data['workspace_id'],
            make_default=serializer.validated_data['make_default'],
        )
        return Response({
            'workspace': WorkspaceSerializer(membership.workspace).data,
            'membership': MembershipSerializer(membership).data,
        })


class MyMembershipListView(V2APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = WorkspaceMembership.objects.filter(
            user=request.user,
            is_active=True,
        ).select_related('workspace', 'user')
        return Response({'memberships': MembershipSerializer(memberships, many=True).data})


class WorkspaceMemberListView(V2APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = resolve_workspace_context(request)
        require_policy(context.membership, Actions.MEMBERSHIP_VIEW)
        memberships = context.workspace.memberships.select_related('workspace', 'user')
        return Response({'memberships': MembershipSerializer(memberships, many=True).data})

    def post(self, request):
        context = resolve_workspace_context(request)
        require_policy(context.membership, Actions.MEMBERSHIP_MANAGE)
        serializer = MembershipCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(get_user_model(), pk=serializer.validated_data['user_id'])
        try:
            membership = create_membership(
                context.membership,
                user,
                serializer.validated_data['role'],
                is_default=serializer.validated_data['is_default'],
            )
        except DjangoValidationError as exc:
            return _validation_error(request, exc)
        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class WorkspaceMemberDetailView(V2APIView):
    permission_classes = [IsAuthenticated]

    def _membership(self, context, membership_id):
        return get_object_or_404(
            WorkspaceMembership.objects.select_related('workspace', 'user'),
            pk=membership_id,
            workspace=context.workspace,
        )

    def patch(self, request, membership_id):
        context = resolve_workspace_context(request)
        require_policy(context.membership, Actions.MEMBERSHIP_MANAGE)
        serializer = MembershipUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = self._membership(context, membership_id)
        try:
            membership = update_membership(
                context.membership,
                membership,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            return _validation_error(request, exc)
        return Response(MembershipSerializer(membership).data)

    def delete(self, request, membership_id):
        context = resolve_workspace_context(request)
        require_policy(context.membership, Actions.MEMBERSHIP_MANAGE)
        membership = self._membership(context, membership_id)
        try:
            delete_membership(context.membership, membership)
        except DjangoValidationError as exc:
            return _validation_error(request, exc)
        return Response(status=status.HTTP_204_NO_CONTENT)
