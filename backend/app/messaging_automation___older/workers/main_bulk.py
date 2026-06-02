from messaging_automation.platforms.bale import BalePlatform
from messaging_automation.workers.bulk_sender import BulkSender


platform = BalePlatform(
    profile_path="profiles/bale_1"
)

platform.login()

sender = BulkSender(platform)

users = [
    "myself2",
    "user2",
    "user3"
]

sender.start(
    users=users,
    text="سلام این یک تست اتوماتیک است",
    delay=10
)

platform.close()