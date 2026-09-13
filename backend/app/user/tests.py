import json

from django.test import TestCase

from user.models import CustomUser


class AuthenticationCharacterizationTests(TestCase):
    def test_registration_creates_authenticated_session(self):
        response = self.client.post(
            '/auth/api/v1/register',
            data=json.dumps({
                'phone_number': '09120000011',
                'name': 'Test User',
                'password': 'strong-test-password',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['redirect'], '/dashboard')
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_login_preserves_legacy_shape(self):
        CustomUser.objects.create_user('09120000012', 'correct-password')
        response = self.client.post(
            '/auth/api/v1/login',
            data=json.dumps({
                'phone_number': '09120000012',
                'password': 'wrong-password',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {'success', 'error'})
        self.assertFalse(response.json()['success'])

    def test_dashboard_redirects_anonymous_user(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.url)
