import os
import unittest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from user.models import CustomUser


@unittest.skipUnless(
    os.getenv('RUN_BROWSER_SMOKE') == '1',
    'Set RUN_BROWSER_SMOKE=1 in an environment with Chromium.',
)
class ActivePageSmokeTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if os.getenv('CHROME_BIN'):
            options.binary_location = os.environ['CHROME_BIN']
        service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))
        cls.browser = webdriver.Chrome(service=service, options=options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = CustomUser.objects.create_user('09120000041', 'test-password')
        self.client.force_login(self.user)
        session_cookie = self.client.cookies['sessionid']
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({
            'name': 'sessionid',
            'value': session_cookie.value,
            'path': '/',
        })

    def test_active_content_and_telegram_pages_render(self):
        for path, element_id in (
            ('/dashboard/content/create/', 'chatInput'),
            ('/dashboard/telegram/channels/', 'getTokenBtn'),
        ):
            with self.subTest(path=path):
                self.browser.get(f'{self.live_server_url}{path}')
                self.assertEqual(self.browser.current_url, f'{self.live_server_url}{path}')
                self.assertTrue(self.browser.find_element(By.ID, element_id).is_displayed())

        self.assertIn(
            '/messaging/api/v1/telegram/request-channel-verification/',
            self.browser.page_source,
        )

    def test_ai_chat_script_uses_characterized_routes(self):
        self.browser.get(f'{self.live_server_url}/static/assets/scripts/ai_chat.js')
        script = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('/content/api/v1/ai/chat/send/', script)
        self.assertIn('/content/api/v1/ai/generate-image/', script)
