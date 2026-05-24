import time
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from messaging_automation.platforms.base_platform import (
    BasePlatform
)

from messaging_automation.services.session_manager import (
    SessionManager
)

logger = logging.getLogger(__name__)


class BalePlatform(BasePlatform):

    BASE_URL = "https://web.bale.ai"

    def __init__(self, account):

        self.account = account

        self.driver = None

    def connect(self):

        self.driver = SessionManager.get_driver(
            self.account,
            headless=False
        )

        self.driver.get(self.BASE_URL)

        time.sleep(5)

    def send_message(
        self,
        recipient,
        message,
        attachment=None
    ):

        logger.info(
            f"ارسال پیام به {recipient}"
        )

        driver = self.driver

        search_box = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/input"
        )

        search_box.clear()

        search_box.send_keys(recipient)

        time.sleep(2)

        user_result = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[2]/div/div[1]/div/div[2]"
        )

        user_result.click()

        time.sleep(2)

        message_input = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[4]/div[4]/div/div[3]/div/div[1]"
        )

        message_input.send_keys(message)

        time.sleep(1)

        message_input.send_keys(Keys.ENTER)

        logger.info(
            f"پیام ارسال شد به {recipient}"
        )

        return True