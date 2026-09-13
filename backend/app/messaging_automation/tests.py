from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from campaigns.models import Campaign, CampaignGoal
from content.models import ContentItem
from messaging_automation.models.channel_verification import ChannelVerification
from messaging_automation.models.telegram_channel import TelegramChannel
from messaging_automation.models.telegram_publish_log import TelegramPublishLog
from messaging_automation.services.telegram_publisher import TelegramPublisher
from user.models import CustomUser


class TelegramCharacterizationTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('09120000031', 'test-password')
        self.goal = CampaignGoal.objects.create(goal='Publish')
        self.campaign = Campaign.objects.create(
            user=self.user,
            title='Campaign',
            main_keyword='main',
            goal=self.goal,
        )
        self.content_item = ContentItem.objects.create(
            campaign=self.campaign,
            title='Generated content',
            information={'generated_content': 'Telegram body'},
        )
        self.channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id='-1001234',
            title='Test channel',
            is_verified=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_verification_request_creates_user_token(self):
        response = self.client.post(
            '/messaging/api/v1/telegram/request-channel-verification/',
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        verification = ChannelVerification.objects.get(token=response.data['token'])
        self.assertEqual(verification.user, self.user)

    @patch('messaging_automation.views.channel_management.TelegramAPI')
    def test_channel_confirmation_persists_verified_channel(self, telegram_api):
        verification = ChannelVerification.objects.create(user=self.user)
        telegram_api.return_value.get_updates.return_value = {
            'ok': True,
            'result': [{
                'channel_post': {
                    'text': verification.token,
                    'message_id': 7,
                    'chat': {
                        'id': -1009876,
                        'title': 'Verified channel',
                        'username': 'verified_channel',
                        'type': 'channel',
                    },
                },
            }],
        }
        response = self.client.post(
            '/messaging/api/v1/telegram/confirm-channel/',
            {'token': verification.token},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        verification.refresh_from_db()
        self.assertTrue(verification.is_verified)
        self.assertTrue(
            TelegramChannel.objects.filter(
                user=self.user,
                chat_id='-1009876',
                is_verified=True,
            ).exists()
        )

    @patch('messaging_automation.services.telegram_publisher.TelegramAPI.send_message')
    def test_publisher_records_success_and_updates_content(self, send_message):
        send_message.return_value = {'ok': True, 'result': {'message_id': 42}}
        result = TelegramPublisher().publish(self.content_item, self.channel)
        self.assertTrue(result['ok'])
        self.content_item.refresh_from_db()
        self.assertEqual(self.content_item.publish_status, 'published')
        self.assertIsNotNone(self.content_item.published_at)
        self.assertEqual(
            TelegramPublishLog.objects.get().status,
            'success',
        )

    @patch('messaging_automation.services.telegram_publisher.TelegramAPI.send_message')
    def test_publisher_records_provider_failure(self, send_message):
        send_message.return_value = {'ok': False, 'description': 'provider failure'}
        with self.assertRaises(RuntimeError):
            TelegramPublisher().publish(self.content_item, self.channel)
        self.assertEqual(TelegramPublishLog.objects.get().status, 'failed')

    @patch('messaging_automation.services.telegram_publisher.TelegramAPI.send_message')
    def test_single_publish_endpoint_and_log_listing(self, send_message):
        send_message.return_value = {'ok': True, 'result': {'message_id': 42}}
        response = self.client.post(
            '/messaging/api/v1/telegram/publish-single/',
            {
                'content_id': self.content_item.id,
                'channel_id': self.channel.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['telegram_message_id'], 42)
        logs_response = self.client.get(
            f'/messaging/api/v1/telegram/logs/{self.content_item.id}/'
        )
        self.assertEqual(logs_response.status_code, 200)
        self.assertEqual(logs_response.data['count'], 1)
        self.assertEqual(logs_response.data['logs'][0]['status'], 'success')

    def test_logs_reject_foreign_content(self):
        other = CustomUser.objects.create_user('09120000032', 'test-password')
        other_campaign = Campaign.objects.create(
            user=other,
            title='Other',
            main_keyword='other',
            goal=self.goal,
        )
        other_content = ContentItem.objects.create(campaign=other_campaign)
        response = self.client.get(
            f'/messaging/api/v1/telegram/logs/{other_content.id}/'
        )
        self.assertEqual(response.status_code, 404)
