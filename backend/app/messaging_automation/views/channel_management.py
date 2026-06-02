from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from messaging_automation.models.telegram_channel import TelegramChannel
from messaging_automation.models.channel_verification import ChannelVerification
from messaging_automation.services.telegram_api import TelegramAPI


class RequestChannelVerificationAPIView(APIView):
    """
    مرحله اول: ساخت توکن تأیید برای کاربر.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        verification = ChannelVerification.objects.create(user=request.user)
        return Response({
            "success": True,
            "token": verification.token
        }, status=status.HTTP_201_CREATED)


class ConfirmChannelAPIView(APIView):
    """
    مرحله دوم: جستجو در آپدیت‌های ربات برای پیدا کردن توکن.
    بعد از تأیید: پیام توکن حذف و پیام خوش‌آمد ارسال می‌شود.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token", "").strip()

        if not token:
            return Response(
                {"success": False, "error": "token الزامی است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # بررسی وجود توکن برای این کاربر
        try:
            verification = ChannelVerification.objects.get(
                token=token,
                user=request.user,
                is_verified=False
            )
        except ChannelVerification.DoesNotExist:
            return Response(
                {"success": False, "error": "توکن معتبر نیست یا قبلاً استفاده شده"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # دریافت آپدیت‌های ربات سراسری
        try:
            api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)
            updates_response = api.get_updates()
        except Exception as e:
            return Response(
                {"success": False, "error": f"خطا در اتصال به تلگرام: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if not updates_response.get("ok"):
            return Response(
                {"success": False, "error": "دریافت آپدیت‌ها از تلگرام ناموفق بود"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # جستجو در channel_post ها برای پیدا کردن توکن
        found_chat = None
        found_message_id = None

        for update in updates_response.get("result", []):
            channel_post = update.get("channel_post")
            if not channel_post:
                continue

            text = channel_post.get("text", "")
            if token not in text:
                continue

            chat = channel_post.get("chat", {})
            if chat.get("type") not in ["channel", "supergroup", "group"]:
                continue

            found_chat = chat
            found_message_id = channel_post.get("message_id")
            break

        if not found_chat:
            return Response(
                {
                    "success": False,
                    "error": (
                        "توکن در هیچ کانال یا گروهی پیدا نشد. "
                        "مطمئن شوید ربات ادمین است و توکن را ارسال کرده‌اید."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ذخیره یا بروزرسانی کانال
        chat_id = str(found_chat.get("id"))
        title = found_chat.get("title", "")
        username = found_chat.get("username")
        chat_type = found_chat.get("type")

        channel, created = TelegramChannel.objects.update_or_create(
            user=request.user,
            chat_id=chat_id,
            defaults={
                "title": title,
                "username": username,
                "channel_type": chat_type,
                "is_verified": True,
                "is_active": True,
            }
        )

        # تأیید verification
        verification.is_verified = True
        verification.save(update_fields=["is_verified"])

        # حذف پیام توکن + ارسال پیام خوش‌آمد
        self._post_verification_actions(api, chat_id, found_message_id, title)

        return Response({
            "success": True,
            "message": "کانال با موفقیت تأیید و اضافه شد",
            "channel": {
                "id": channel.id,
                "chat_id": channel.chat_id,
                "title": channel.title,
                "username": channel.username,
                "channel_type": channel.channel_type,
                "is_new": created,
            }
        }, status=status.HTTP_200_OK)

    def _post_verification_actions(
        self,
        api: TelegramAPI,
        chat_id: str,
        message_id: int,
        channel_title: str
    ):
        """
        حذف پیام توکن و ارسال پیام تأیید در کانال.
        خطاها را نادیده می‌گیریم تا فرآیند اصلی متوقف نشود.
        """
        # حذف پیام توکن
        if message_id:
            try:
                api.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"⚠️ delete token message failed: {e}")

        # ارسال پیام خوش‌آمد
        try:
            welcome_text = (
                "✅ <b>اتصال موفق</b>\n\n"
                f"کانال <b>{channel_title}</b> با موفقیت به پنل ابریت کلود متصل شد.\n\n"
                "از این پس محتوای تولید شده توسط هوش مصنوعی "
                "به صورت خودکار در این کانال منتشر خواهد شد. 🚀"
            )
            api.send_message(chat_id, welcome_text)
        except Exception as e:
            print(f"⚠️ send welcome message failed: {e}")


class UserChannelsAPIView(APIView):
    """لیست کانال‌های کاربر"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        channels = TelegramChannel.objects.filter(
            user=request.user,
            is_verified=True,
            is_active=True
        ).order_by("-created_at")

        return Response({
            "count": channels.count(),
            "channels": [
                {
                    "id": c.id,
                    "chat_id": c.chat_id,
                    "title": c.title,
                    "username": c.username,
                    "channel_type": c.channel_type,
                }
                for c in channels
            ]
        })

    def delete(self, request, channel_id):
        try:
            channel = TelegramChannel.objects.get(
                id=channel_id,
                user=request.user
            )
            channel.delete()
            return Response({"success": True})
        except TelegramChannel.DoesNotExist:
            return Response(
                {"error": "کانال پیدا نشد"},
                status=status.HTTP_404_NOT_FOUND
            )


class PublishToChannelsAPIView(APIView):
    """ارسال محتوا به یک یا چند کانال انتخابی"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from content.models import ContentItem
        from messaging_automation.services.telegram_publisher import TelegramPublisher

        content_id = request.data.get("content_id")
        channel_ids = request.data.get("channel_ids", [])

        if not content_id or not channel_ids:
            return Response(
                {"error": "content_id و channel_ids الزامی هستند"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_item = ContentItem.objects.get(id=content_id)
        except ContentItem.DoesNotExist:
            return Response(
                {"error": "محتوا پیدا نشد"},
                status=status.HTTP_404_NOT_FOUND
            )

        info = content_item.information or {}
        if not info.get("generated_content"):
            return Response(
                {"error": "محتوای تولید شده‌ای وجود ندارد"},
                status=status.HTTP_400_BAD_REQUEST
            )

        channels = TelegramChannel.objects.filter(
            id__in=channel_ids,
            user=request.user,
            is_verified=True,
            is_active=True
        )

        if not channels.exists():
            return Response(
                {"error": "کانال معتبری پیدا نشد"},
                status=status.HTTP_400_BAD_REQUEST
            )

        publisher = TelegramPublisher()
        results = []

        for channel in channels:
            try:
                publisher.publish(content_item, channel)
                results.append({
                    "channel_id": channel.id,
                    "title": channel.title,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "channel_id": channel.id,
                    "title": channel.title,
                    "success": False,
                    "error": str(e)
                })

        return Response({
            "success": all(r["success"] for r in results),
            "results": results
        })