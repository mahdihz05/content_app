import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class SessionManager:

    _drivers = {}

    @classmethod
    def get_profile_path(cls, account):

        profile_root = Path("/app/browser_profiles")

        profile_root.mkdir(
            parents=True,
            exist_ok=True
        )

        profile_path = profile_root / (
            f"{account.platform}_{account.id}"
        )

        profile_path.mkdir(
            parents=True,
            exist_ok=True
        )

        return str(profile_path)

    @classmethod
    def get_driver(
            cls,
            account,
            headless=False
    ):

        cache_key = (
            f"{account.platform}_{account.id}"
        )

        existing_driver = cls._drivers.get(
            cache_key
        )

        if existing_driver:

            try:

                # تست زنده بودن درایور
                existing_driver.current_url

                return existing_driver

            except Exception:

                try:
                    existing_driver.quit()
                except Exception:
                    pass

                cls._drivers.pop(
                    cache_key,
                    None
                )

        profile_path = cls.get_profile_path(
            account
        )

        driver = cls.create_driver(
            profile_path=profile_path,
            headless=headless
        )

        cls._drivers[cache_key] = driver

        return driver

    @classmethod
    def create_driver(
            cls,
            profile_path,
            headless=False
    ):

        os.makedirs(
            profile_path,
            exist_ok=True
        )

        # =====================================================
        # CHROME OPTIONS
        # =====================================================

        options = Options()

        chrome_bin = os.getenv(
            "CHROME_BIN",
            "/usr/bin/chromium"
        )

        chromedriver_path = os.getenv(
            "CHROMEDRIVER_PATH",
            "/usr/bin/chromedriver"
        )

        options.binary_location = chrome_bin

        # =====================================================
        # PROFILE
        # =====================================================

        # این بخش خیلی مهمه
        # بدون این پروفایل ذخیره نمیشه
        options.add_argument(
            f"--user-data-dir={profile_path}"
        )

        options.add_argument(
            "--profile-directory=Default"
        )

        # =====================================================
        # DOCKER FIXES
        # =====================================================

        options.add_argument(
            "--no-sandbox"
        )

        options.add_argument(
            "--disable-dev-shm-usage"
        )

        options.add_argument(
            "--disable-gpu"
        )

        options.add_argument(
            "--disable-setuid-sandbox"
        )

        options.add_argument(
            "--disable-extensions"
        )

        options.add_argument(
            "--disable-infobars"
        )

        options.add_argument(
            "--window-size=1920,1080"
        )

        options.add_argument(
            "--lang=fa"
        )

        options.add_argument(
            "--remote-allow-origins=*"
        )

        # =====================================================
        # HEADLESS
        # =====================================================

        if headless:

            # فقط همین حالت جدید
            options.add_argument(
                "--headless=new"
            )

        # =====================================================
        # STABILITY
        # =====================================================

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-automation"]
        )

        options.add_experimental_option(
            "useAutomationExtension",
            False
        )

        # =====================================================
        # CHROMEDRIVER
        # =====================================================

        service = Service(
            executable_path=chromedriver_path
        )

        try:

            print("=" * 60)
            print("STARTING CHROME DRIVER")
            print("=" * 60)

            print(f"CHROME_BIN: {chrome_bin}")
            print(f"CHROMEDRIVER: {chromedriver_path}")
            print(f"PROFILE PATH: {profile_path}")
            print(f"HEADLESS: {headless}")

            driver = webdriver.Chrome(
                service=service,
                options=options
            )

            print("CHROME DRIVER STARTED SUCCESSFULLY")

            return driver

        except Exception as e:

            print("=" * 60)
            print("FAILED TO START CHROME")
            print("=" * 60)

            print(type(e).__name__)
            print(str(e))

            print("=" * 60)

            raise

    @classmethod
    def close_driver(cls, account):

        cache_key = (
            f"{account.platform}_{account.id}"
        )

        driver = cls._drivers.get(
            cache_key
        )

        if driver:

            try:

                driver.quit()

            except Exception:
                pass

            cls._drivers.pop(
                cache_key,
                None
            )

    @classmethod
    def close_all(cls):

        for key, driver in list(
                cls._drivers.items()
        ):

            try:

                driver.quit()

            except Exception:
                pass

        cls._drivers = {}