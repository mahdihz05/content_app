import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from messaging_automation.platforms.base import BasePlatform

from messaging_automation.core.browser import BrowserManager
from messaging_automation.core.actions import (
    safe_click,
    safe_send_keys
)
from messaging_automation.core.logger import setup_logger


class BalePlatform(BasePlatform):

    def __init__(
            self,
            profile_path="profiles/bale_1",
            headless=False
    ):

        self.logger = setup_logger("bale")

        self.driver = BrowserManager.create(
            profile_path=profile_path,
            headless=headless
        )

    def open(self):

        self.logger.info("OPEN BALE")

        self.driver.get("https://web.bale.ai")

        time.sleep(5)

    def login(self):

        self.open()

        self.logger.info(
            "اگر لاگین نیستی دستی لاگین کن"
        )

        input("بعد از لاگین Enter بزن...")

        self.logger.info("LOGIN SUCCESS")

    def search_user(self, username):

        self.logger.info(
            f"SEARCH USER -> {username}"
        )

        safe_click(
            self.driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div",
            self.logger,
            "search button"
        )

        search_box = safe_send_keys(
            self.driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/input",
            username,
            self.logger,
            "search input"
        )

        time.sleep(3)

        safe_click(
            self.driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[2]/div/div[1]/div/div[2]",
            self.logger,
            "search result"
        )
        self.logger.info(
            f"USER FOUND -> {username}"
        )

    def send_message(self, user, text):
        self.logger.info(
            f"SEND MESSAGE -> user={user}"
        )

        self.search_user(user)

        message_box = safe_send_keys(
            self.driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[4]/div[4]/div/div[3]/div/div[1]",
            text,
            self.logger,
            "message input"
        )

        message_box.send_keys(Keys.ENTER)

        self.logger.info(
            f"MESSAGE SENT -> user={user}"
        )

        time.sleep(2)

    def get_unread_messages(self):
        self.logger.info(
            "CHECK UNREAD MESSAGES"
        )

        # فعلاً mock
        # بعداً باید unread chats را بخوانی

        return []



    def reply_to_message(self, message, text):

        self.logger.info(
            f"REPLY MESSAGE -> {text}"
        )

        # بعداً کامل می‌شود

    def close(self):

        self.logger.info("CLOSE DRIVER")

        self.driver.quit()