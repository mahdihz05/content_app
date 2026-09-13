from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from content.models import ContentItem
from messaging_automation.models.telegram_publish_log import TelegramPublishLog
from workspaces.access import require_workspace_action
from workspaces.policy import Actions


class PublishLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, content_id):
        workspace = require_workspace_action(request, Actions.CONTENT_VIEW).workspace

        try:
            content_item = ContentItem.objects.get(
                id=content_id,
                workspace=workspace,
            )
        except ContentItem.DoesNotExist:
            return Response(
                {"error": "محتوا یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )

        logs = (
            TelegramPublishLog.objects
            .filter(content_item=content_item, workspace=workspace)
            .select_related("channel")
            .order_by("-created_at")
        )

        return Response({
            "content_id": content_id,
            "count": logs.count(),
            "logs": [
                {
                    "id": log.id,
                    "status": log.status,
                    "channel": {
                        "id": log.channel.id,
                        "title": log.channel.title,
                    },
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ]
        })
