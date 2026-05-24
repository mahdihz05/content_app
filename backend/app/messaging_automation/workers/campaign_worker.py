import threading
import logging

from messaging_automation.services.bulk_sender import (
    BulkSenderService
)

logger = logging.getLogger(__name__)


class CampaignWorker:

    @classmethod
    def start_campaign(
        cls,
        campaign
    ):

        thread = threading.Thread(
            target=cls.run_campaign,
            args=(campaign,),
            daemon=True
        )

        thread.start()

        return thread

    @classmethod
    def run_campaign(
        cls,
        campaign
    ):

        try:

            service = BulkSenderService(
                campaign
            )

            service.run()

        except Exception as e:

            logger.exception(e)