from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from content.models import ContentItem
from messaging_automation.models.telegram_channel import TelegramChannel
from messaging_automation.services.telegram_publisher import TelegramPublisher


class PublishToTelegramAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        content_id = request.data.get("content_id")
        channel_id = request.data.get("channel_id")

        if not content_id or not channel_id:
            return Response(
                {"error": "content_id و channel_id الزامی هستند"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_item = ContentItem.objects.get(
                id=content_id,
                campaign__user=request.user
            )
        except ContentItem.DoesNotExist:
            return Response(
                {"error": "محتوا یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            channel = TelegramChannel.objects.get(
                id=channel_id,
                user=request.user,
                is_verified=True,
                is_active=True
            )
        except TelegramChannel.DoesNotExist:
            return Response(
                {"error": "کانال یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )

        info = content_item.information or {}
        if not info.get("generated_content"):
            return Response(
                {"error": "محتوای تولید شده‌ای وجود ندارد"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            publisher = TelegramPublisher()
            result = publisher.publish(content_item, channel)

            return Response({
                "success": True,
                "message": "محتوا با موفقیت منتشر شد",
                "telegram_message_id": result.get("result", {}).get("message_id"),
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "chat_id": channel.chat_id
                }
            }, status=status.HTTP_200_OK)

        except RuntimeError as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception as e:
            import traceback
            print(f"❌ publish error:\n{traceback.format_exc()}")
            return Response(
                {"success": False, "error": f"خطای داخلی: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )