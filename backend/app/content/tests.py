from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from campaigns.models import Campaign, CampaignGoal
from content.models import AIChatSession, AIMessage, ContentItem, Keyword
from user.models import CustomUser


class ContentCharacterizationTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('09120000021', 'test-password')
        self.other_user = CustomUser.objects.create_user('09120000022', 'test-password')
        self.goal = CampaignGoal.objects.create(goal='Awareness')
        self.campaign = Campaign.objects.create(
            user=self.user,
            title='Campaign',
            main_keyword='main',
            goal=self.goal,
        )
        self.other_campaign = Campaign.objects.create(
            user=self.other_user,
            title='Other campaign',
            main_keyword='other',
            goal=self.goal,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_content_persists_primary_keyword(self):
        response = self.client.post('/content/api/v1/content/', {
            'campaign_id': self.campaign.id,
            'title': 'Characterized content',
            'main_keyword': 'baseline',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        item = ContentItem.objects.get(pk=response.data['content_item_id'])
        keyword = Keyword.objects.get(content_item=item)
        self.assertEqual(keyword.keyword, 'baseline')
        self.assertEqual(keyword.source, 'user_input')

    def test_create_content_rejects_foreign_campaign(self):
        response = self.client.post('/content/api/v1/content/', {
            'campaign_id': self.other_campaign.id,
            'title': 'Blocked',
            'main_keyword': 'blocked',
        }, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(ContentItem.objects.filter(title='Blocked').exists())

    @patch('content.views.ai_chat.ConversationOrchestrator.process_message')
    def test_chat_persists_user_and_assistant_messages(self, process_message):
        process_message.return_value = {'message': 'Assistant reply'}
        response = self.client.post('/content/api/v1/ai/chat/send/', {
            'message': 'User message',
            'campaign_id': self.campaign.id,
            'platform': 'website',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        session = AIChatSession.objects.get(pk=response.data['session_id'])
        self.assertEqual(
            list(AIMessage.objects.filter(session=session).values_list('role', 'content')),
            [('user', 'User message'), ('assistant', 'Assistant reply')],
        )

    @patch(
        'content.views.ai_chat.PromptService.build_content_generation_prompt',
        create=True,
    )
    @patch('content.views.ai_chat.AITextService.generate_text', create=True)
    def test_final_generation_persists_legacy_json(self, generate_text, build_prompt):
        build_prompt.return_value = 'Baseline prompt'
        generate_text.return_value = 'Generated baseline text'
        item = ContentItem.objects.create(
            campaign=self.campaign,
            title='Draft',
            main_keyword='baseline',
            information={},
        )
        response = self.client.post('/content/api/v1/ai/generate-content/', {
            'content_id': item.id,
        }, format='json')
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.status, 'completed')
        self.assertEqual(item.information['generated_content'], 'Generated baseline text')
