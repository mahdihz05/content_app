from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import Resolver404, resolve

from common.feature_flags import is_feature_enabled
from user.models import CustomUser


class CorrelationAndV2ContractTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('09120000001', 'test-password')

    def test_correlation_id_is_generated_for_legacy_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers['X-Correlation-ID'])

    def test_safe_correlation_id_is_propagated(self):
        response = self.client.get('/', HTTP_X_CORRELATION_ID='test-request-123')
        self.assertEqual(response.headers['X-Correlation-ID'], 'test-request-123')

    def test_unsafe_correlation_id_is_replaced(self):
        response = self.client.get('/', HTTP_X_CORRELATION_ID='invalid value')
        self.assertNotEqual(response.headers['X-Correlation-ID'], 'invalid value')

    def test_health_requires_authentication_with_v2_error_contract(self):
        response = self.client.get('/api/v2/health/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error']['code'], 'authentication_required')
        self.assertEqual(
            response.json()['error']['correlation_id'],
            response.headers['X-Correlation-ID'],
        )

    def test_authenticated_health_and_readiness(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/v2/health/').status_code, 200)
        self.assertEqual(self.client.get('/api/v2/readiness/').status_code, 200)

    def test_readiness_does_not_leak_database_error(self):
        self.client.force_login(self.user)
        with patch('common.views.database_is_ready', return_value=False):
            response = self.client.get('/api/v2/readiness/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['error']['code'], 'service_not_ready')


class FeatureFlagTests(TestCase):
    @override_settings(V2_FEATURE_FLAGS=set())
    def test_unknown_flags_are_disabled(self):
        self.assertFalse(is_feature_enabled('unknown', workspace=object()))

    @override_settings(V2_FEATURE_FLAGS={'content_history'})
    def test_explicit_flag_is_enabled(self):
        self.assertTrue(is_feature_enabled('content_history'))


class RouteInventoryTests(TestCase):
    def test_documented_active_routes_resolve(self):
        expected_names = {
            '/': 'landing',
            '/auth/login': 'login',
            '/dashboard/': 'dashboard',
            '/dashboard/content/create/': 'create-content-page',
            '/content/api/v1/ai/chat/send/': 'ai_send_message',
            '/messaging/api/v1/telegram/channels/': 'telegram-channels',
            '/api/v2/health/': 'health',
        }
        for path, expected_name in expected_names.items():
            with self.subTest(path=path):
                self.assertEqual(resolve(path).url_name, expected_name)

    def test_documented_stale_browser_routes_do_not_resolve(self):
        for path in (
            '/content/api/v1/get-content-items/',
            '/content/api/v1/ai/generate-image/',
            '/ai/chat/',
        ):
            with self.subTest(path=path), self.assertRaises(Resolver404):
                resolve(path)
