import json

from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from automation.callbacks import accept_callback
from automation.exceptions import AutomationError
from automation.models import ActionApproval, AutomationCommand
from automation.services import decide_approval
from common.api import V2APIView, error_payload


def _workspace_matches(request, obj):
    return request.headers.get('X-Workspace-ID', '') == str(obj.workspace.public_id)


def _has_workspace_access(request, obj):
    return request.user.workspace_memberships.filter(
        workspace=obj.workspace,
        is_active=True,
    ).exists()


def _can_read(request, obj, actor_field):
    return (
        _workspace_matches(request, obj)
        and _has_workspace_access(request, obj)
        and (
            getattr(obj, f'{actor_field}_id') == request.user.pk
            or request.user.has_perm('automation.decide_actionapproval')
        )
    )


class CommandStatusView(V2APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, public_id):
        try:
            command = AutomationCommand.objects.select_related('workspace').get(public_id=public_id)
        except AutomationCommand.DoesNotExist as exc:
            raise NotFound from exc
        if not _can_read(request, command, 'actor'):
            raise NotFound
        return Response({
            'contract_version': 'v1',
            'command': {
                'id': str(command.public_id),
                'workspace_id': str(command.workspace.public_id),
                'tool_name': command.tool_name,
                'tool_version': command.tool_version,
                'effect': command.effect,
                'status': command.status,
                'result': command.result,
                'error_code': command.error_code,
                'created_at': command.created_at.isoformat(),
                'updated_at': command.updated_at.isoformat(),
            },
        })


class ApprovalStatusView(V2APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, public_id):
        try:
            approval = ActionApproval.objects.select_related('workspace').get(public_id=public_id)
        except ActionApproval.DoesNotExist as exc:
            raise NotFound from exc
        if not _can_read(request, approval, 'requested_by'):
            raise NotFound
        return Response({
            'contract_version': 'v1',
            'approval': {
                'id': str(approval.public_id),
                'workspace_id': str(approval.workspace.public_id),
                'tool_name': approval.tool_name,
                'tool_version': approval.tool_version,
                'status': approval.status,
                'reason': approval.reason,
                'expires_at': approval.expires_at.isoformat(),
                'created_at': approval.created_at.isoformat(),
                'updated_at': approval.updated_at.isoformat(),
            },
        })


class ApprovalDecisionView(V2APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, public_id):
        if not request.user.has_perm('automation.decide_actionapproval'):
            return Response(
                error_payload(request, 'permission_denied', 'Approval authority is required.'),
                status=403,
            )
        try:
            approval = ActionApproval.objects.select_related('workspace').get(public_id=public_id)
        except ActionApproval.DoesNotExist as exc:
            raise NotFound from exc
        if not _workspace_matches(request, approval) or not _has_workspace_access(request, approval):
            raise NotFound
        decision = request.data.get('decision')
        if decision not in {'approve', 'reject'}:
            return Response(
                error_payload(request, 'contract_invalid', 'decision must be approve or reject.'),
                status=400,
            )
        try:
            approval = decide_approval(
                approval=approval,
                reviewer=request.user,
                approve=decision == 'approve',
                reason=str(request.data.get('reason', ''))[:2000],
                correlation_id=getattr(request, 'correlation_id', ''),
            )
        except AutomationError as exc:
            return Response(error_payload(request, exc.code, str(exc)), status=409)
        return Response({'contract_version': 'v1', 'approval_id': str(approval.public_id), 'status': approval.status})


class ExecutionCallbackView(V2APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            body = json.loads(request.body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return Response(error_payload(request, 'contract_invalid', 'Body must be JSON.'), status=400)
        try:
            execution, duplicate = accept_callback(
                grant=request.headers.get('X-Automation-Grant', ''),
                timestamp=request.headers.get('X-Automation-Timestamp', ''),
                nonce=request.headers.get('X-Automation-Nonce', ''),
                idempotency_key=request.headers.get('Idempotency-Key', ''),
                signature=request.headers.get('X-Automation-Signature', ''),
                body=body,
                correlation_id=getattr(request, 'correlation_id', ''),
            )
        except AutomationError as exc:
            status_code = 409 if exc.code == 'callback_replay' else 401
            return Response(error_payload(request, exc.code, str(exc)), status=status_code)
        return Response({
            'contract_version': 'v1',
            'execution_id': str(execution.public_id),
            'status': execution.status,
            'duplicate': duplicate,
        })
