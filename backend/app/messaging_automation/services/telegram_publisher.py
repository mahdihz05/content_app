from django.conf import settings
from django.utils import timezone

from messaging_automation.models.telegram_publish_log import TelegramPublishLog
from messaging_automation.services.telegram_api import TelegramAPI


class TelegramPublisher:

    def __init__(self):
        self.api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)

    def publish(self, content_item, channel):
        information = content_item.information or {}
        generated_content = information.get("generated_content", "")
        image_url = information.get("image_url")
        video_url = information.get("video_url")

        try:
            if video_url:
                result = self.api.send_video(
                    chat_id=channel.chat_id,
                    video_url=video_url,
                    caption=generated_content
                )
            elif image_url:
                result = self.api.send_photo(
                    chat_id=channel.chat_id,
                    photo_url=image_url,
                    caption=generated_content
                )
            else:
                result = self.api.send_message(
                    chat_id=channel.chat_id,
                    text=generated_content
                )

            if not result.get("ok"):
                error_msg = result.get("description", "Unknown Telegram error")
                self._save_log(content_item, channel, "failed", result, error_msg)
                raise RuntimeError(f"Telegram API error: {error_msg}")

            self._save_log(content_item, channel, "success", result)
            content_item.publish_status = "published"
            content_item.published_at = timezone.now()
            content_item.save(update_fields=["publish_status", "published_at"])
            return result

        except RuntimeError:
            raise
        except Exception as e:
            self._save_log(content_item, channel, "failed", error_message=str(e))
            content_item.publish_status = "publish_failed"
            content_item.save(update_fields=["publish_status"])
            raise RuntimeError(f"publish failed: {str(e)}")

    def _save_log(self, content_item, channel, status,
                  response_json=None, error_message=None):
        try:
            TelegramPublishLog.objects.create(
                content_item=content_item,
                channel=channel,
                status=status,
                response_json=response_json,
                error_message=error_message
            )
        except Exception as e:
            print(f"❌ log save error: {e}")