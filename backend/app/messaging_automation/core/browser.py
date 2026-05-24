import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BrowserManager:

    @staticmethod
    def create(profile_path=None, headless=False):

        options = webdriver.ChromeOptions()

        # جلوگیری از بسته شدن مرورگر
        options.add_experimental_option("detach", True)

        # پایداری بیشتر
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")

        # جلوگیری از crash
        options.add_argument("--disable-gpu")

        # جلوگیری از detection
        options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )

        # maximize
        options.add_argument("--start-maximized")

        # headless
        if headless:
            options.add_argument("--headless=new")

        # ساخت پوشه profile اگر وجود ندارد
        if profile_path:

            absolute_profile = os.path.abspath(profile_path)

            os.makedirs(absolute_profile, exist_ok=True)

            print("PROFILE PATH:")
            print(absolute_profile)

            options.add_argument(
                f"--user-data-dir={absolute_profile}"
            )

        print("STARTING CHROME...")

        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        print("CHROME STARTED SUCCESSFULLY")

        return driver