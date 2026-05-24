import threading

from messaging_automation.services.bulk_sender import BulkSender


def start_campaign(platform, campaign):

    sender = BulkSender(platform, campaign)

    thread = threading.Thread(
        target=sender.start
    )

    thread.start()

    return thread