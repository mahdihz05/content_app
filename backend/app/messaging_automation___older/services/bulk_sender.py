import time
import logging

from django.utils import timezone

from messaging_automation.models import (
    CampaignRecipient
)

from messaging_automation.models.message_log import (
    MessageLog
)

from messaging_automation.platforms.bale_platform import (
    BalePlatform
)

logger = logging.getLogger(__name__)


class BulkSenderService:

    def __init__(self, campaign):

        self.campaign = campaign

        self.account = campaign.account

        self.platform = self.get_platform()

    def get_platform(self):

        if self.account.platform == "bale":

            return BalePlatform(
                self.account
            )

        raise Exception(
            f"پلتفرم پشتیبانی نمی‌شود: {self.account.platform}"
        )

    def run(self):

        logger.info(
            f"شروع کمپین {self.campaign.id}"
        )

        self.campaign.status = "running"

        self.campaign.save(
            update_fields=["status"]
        )

        self.platform.connect()

        recipients = CampaignRecipient.objects.filter(
            campaign=self.campaign,
            status="pending"
        )

        success_count = 0
        failed_count = 0

        for recipient in recipients:

            try:

                self.platform.send_message(
                    recipient=recipient.recipient,
                    message=self.campaign.message,
                )

                recipient.status = "sent"

                recipient.sent_at = timezone.now()

                recipient.save(
                    update_fields=[
                        "status",
                        "sent_at"
                    ]
                )

                MessageLog.objects.create(
                    campaign=self.campaign,
                    sender=self.account.name,
                    receiver=recipient.recipient,
                    message=self.campaign.message,
                )

                success_count += 1

            except Exception as e:

                logger.exception(e)

                recipient.status = "failed"

                recipient.error_message = str(e)

                recipient.save(
                    update_fields=[
                        "status",
                        "error_message"
                    ]
                )

                failed_count += 1

            delay = self.campaign.delay_between_messages

            time.sleep(delay)

        self.campaign.status = "completed"

        self.campaign.save(
            update_fields=["status"]
        )

        logger.info(
            f"""
            کمپین پایان یافت
            success={success_count}
            failed={failed_count}
            """
        )

        return {
            "success": success_count,
            "failed": failed_count,
        }