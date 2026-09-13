# campaigns/views.py
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from campaigns.models import Campaign
from content.models import ContentItem, Keyword, AIChatSession, AIMessage
from research.models import ResearchSource
from utils.api_response import api_response
from ai.services.prompt_service import PromptService
from ai.services.ai_text_service import AITextService
from ai.services.ai_service import AIService
from ai.orchestration.conversation_orchestrator import ConversationOrchestrator
from workspaces.access import require_workspace_action
from workspaces.policy import Actions


# ============================================================
# AI Chat Interface - صفحه اصلی و مدیریت Session
# ============================================================

class AIStartSession(LoginRequiredMixin, TemplateView):
    """
    صفحه اصلی چت AI
    نمایش رابط کاربری چت و لیست کمپین‌های کاربر
    """
    template_name = 'campaigns/ai_chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = require_workspace_action(self.request, Actions.CONTENT_VIEW).workspace
        context['campaigns'] = Campaign.objects.filter(
            workspace=workspace
        ).order_by('-created_at')
        return context


class AISendMessage(APIView):
    """
    ارسال پیام به AI و دریافت پاسخ
    مدیریت session، content_item و پردازش با Orchestrator
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
        message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id')
        content_item_id = request.data.get('content_item_id')
        campaign_id = request.data.get('campaign_id')
        platform = request.data.get('platform', 'website')

        # اعتبارسنجی پیام
        if not message:
            return Response(
                {'error': 'پیام نمی‌تواند خالی باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(message) > 5000:
            return Response(
                {'error': 'پیام نباید بیشتر از 5000 کاراکتر باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # اعتبارسنجی platform
        if not platform:
            return Response(
                {'error': 'پلتفرم الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # مدیریت Session
            session = self._get_or_create_session(session_id, request.user, workspace)

            # مدیریت ContentItem با platform
            content_item = self._get_or_create_content_item(
                content_item_id,
                campaign_id,
                request.user,
                workspace,
                platform
            )

            # اتصال session به content_item
            if content_item and not session.content_item:
                session.content_item = content_item
                session.save(update_fields=['content_item'])

            # ذخیره پیام کاربر
            AIMessage.objects.create(
                session=session,
                role='user',
                content=message
            )

            # پردازش با Orchestrator
            orchestrator = ConversationOrchestrator(
                user=request.user,
                session=session,
                content_item=content_item
            )

            response_data = orchestrator.process_message(message)

            # بررسی ایمن پاسخ
            if not response_data or not isinstance(response_data, dict):
                raise ValueError("پاسخ نامعتبر از Orchestrator")

            # دریافت message با fallback
            ai_message = response_data.get('message') or response_data.get('reply', 'پاسخی دریافت نشد')

            # ذخیره پاسخ AI
            AIMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_message
            )

            # ساخت پاسخ نهایی با مقادیر ایمن
            final_response = {
                'message': ai_message,
                'session_id': session.id,
                'content_item_id': content_item.id if content_item else None,
                'metadata': response_data.get('metadata') or {},
                'actions': response_data.get('actions') or [],
                'next_step': response_data.get('next_step', ''),
            }

            # اضافه کردن اطلاعات content_item به صورت خلاصه
            if content_item:
                final_response['content_item'] = {
                    'id': content_item.id,
                    'title': content_item.title,
                    'status': content_item.status,
                    'platform': content_item.platform,
                    'main_keyword': content_item.main_keyword or ''
                }

            return Response(final_response, status=status.HTTP_200_OK)

        except Campaign.DoesNotExist:
            return Response(
                {'error': 'کمپین مورد نظر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ContentItem.DoesNotExist:
            return Response(
                {'error': 'محتوای مورد نظر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # لاگ کامل خطا
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ خطا در AISendMessage:\n{error_trace}")

            return Response(
                {'error': f'خطا در پردازش پیام: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_or_create_session(self, session_id, user, workspace):
        """دریافت یا ایجاد session"""
        if session_id:
            try:
                return AIChatSession.objects.get(id=session_id, workspace=workspace)
            except AIChatSession.DoesNotExist:
                pass

        return AIChatSession.objects.create(user=user, workspace=workspace)

    def _get_or_create_content_item(self, content_item_id, campaign_id, user, workspace, platform='website'):
        """دریافت یا ایجاد content_item با platform"""
        if content_item_id:
            try:
                return ContentItem.objects.get(
                    id=content_item_id,
                    workspace=workspace,
                )
            except ContentItem.DoesNotExist:
                pass

        if campaign_id:
            campaign = Campaign.objects.get(id=campaign_id, workspace=workspace)
            return ContentItem.objects.create(
                campaign=campaign,
                title='محتوای جدید',
                main_keyword='',
                status='draft',
                platform=platform,
                language='fa'
            )

        return None
class AIGenerateImage(APIView):
    """
    تولید تصویر با AI و ذخیره در session
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
        prompt = request.data.get('prompt', '').strip()
        session_id = request.data.get('session_id')
        size = request.data.get('size', '1024x1024')

        # اعتبارسنجی prompt
        if not prompt:
            return Response(
                {'error': 'پرامپت تصویر نمی‌تواند خالی باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(prompt) > 1000:
            return Response(
                {'error': 'پرامپت نباید بیشتر از 1000 کاراکتر باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # اعتبارسنجی size
        valid_sizes = ['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792']
        if size not in valid_sizes:
            return Response(
                {'error': f'سایز باید یکی از این مقادیر باشد: {", ".join(valid_sizes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # مدیریت Session
            session = self._get_or_create_session(session_id, request.user, workspace)

            # ذخیره پیام کاربر (درخواست تصویر)
            user_message = AIMessage.objects.create(
                session=session,
                role='user',
                content=prompt,
                message_type='text'
            )

            # تولید تصویر با AI
            ai_service = AIService()
            image_url = ai_service.generate_image(prompt=prompt, size=size)

            # ذخیره پاسخ AI (URL تصویر)
            ai_message = AIMessage.objects.create(
                session=session,
                role='assistant',
                content=image_url,
                message_type='image',
                metadata={
                    'prompt': prompt,
                    'size': size,
                    'generated_at': timezone.now().isoformat()
                }
            )

            return Response({
                'session_id': session.id,
                'image_url': image_url,
                'message_id': ai_message.id,
                'prompt': prompt,
                'size': size,
                'message': 'تصویر با موفقیت تولید شد'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ خطا در تولید تصویر:\n{error_trace}")

            return Response(
                {'error': f'خطا در تولید تصویر: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_or_create_session(self, session_id, user, workspace):
        """دریافت یا ایجاد session"""
        if session_id:
            try:
                return AIChatSession.objects.get(id=session_id, workspace=workspace)
            except AIChatSession.DoesNotExist:
                pass

        return AIChatSession.objects.create(user=user, workspace=workspace)


class AISessionHistory(APIView):
    """
    دریافت تاریخچه کامل یک session
    شامل پیام‌ها و اطلاعات content_item
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        workspace = require_workspace_action(request, Actions.CONTENT_VIEW).workspace
        try:
            session = AIChatSession.objects.select_related(
                'content_item',
                'content_item__campaign'
            ).get(id=session_id, workspace=workspace)

            # دریافت پیام‌ها
            # دریافت پیام‌ها (شامل تصاویر)
            messages = AIMessage.objects.filter(
                session=session
            ).order_by('created_at').values(
                'id', 'role', 'content', 'message_type', 'metadata', 'created_at'
            )

            messages_data = [
                {
                    'id': msg['id'],
                    'role': msg['role'],
                    'content': msg['content'],
                    'message_type': msg['message_type'],
                    'metadata': msg['metadata'] or {},
                    'created_at': msg['created_at'].isoformat()
                }
                for msg in messages
            ]

            # اطلاعات content_item
            content_item_data = None
            if session.content_item:
                item = session.content_item
                keywords = Keyword.objects.filter(
                    content_item=item
                ).values('id', 'keyword', 'source')

                content_item_data = {
                    'id': item.id,
                    'title': item.title,
                    'main_keyword': item.main_keyword,
                    'additional_keywords': item.additional_keywords,
                    'description': item.description,
                    'goal': item.goal,
                    'platform': item.platform,
                    'language': item.language,
                    'status': item.status,
                    'campaign': {
                        'id': item.campaign.id,
                        'title': item.campaign.title
                    } if item.campaign else None,
                    'keywords': list(keywords)
                }

            return Response({
                'session_id': session.id,
                'messages': messages_data,
                'content_item': content_item_data,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }, status=status.HTTP_200_OK)

        except AIChatSession.DoesNotExist:
            return Response(
                {'error': 'Session یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )


class AINewConversation(APIView):
    """شروع مکالمه جدید"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
        campaign_id = request.data.get('campaign_id')
        platform = request.data.get('platform', 'website')

        try:
            session = AIChatSession.objects.create(user=request.user, workspace=workspace)

            content_item = None
            if campaign_id:
                campaign = Campaign.objects.get(id=campaign_id, workspace=workspace)
                content_item = ContentItem.objects.create(
                    campaign=campaign,
                    title='محتوای جدید',
                    main_keyword='',
                    status='draft',
                    platform=platform,
                    language='fa'
                )
                session.content_item = content_item
                session.save(update_fields=['content_item'])

            return Response({
                'session_id': session.id,
                'content_item_id': content_item.id if content_item else None,
                'message': 'مکالمه جدید آغاز شد'
            }, status=status.HTTP_201_CREATED)

        except Campaign.DoesNotExist:
            return Response(
                {'error': 'کمپین یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================
# ContentItem CRUD - مدیریت کامل محتوا
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_content_item(request):
    """
    ساخت ContentItem جدید
    الزامی: campaign_id, title, main_keyword
    """
    campaign_id = request.data.get('campaign_id')
    workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
    title = request.data.get('title', '').strip()
    main_keyword = request.data.get('main_keyword', '').strip()

    if not all([campaign_id, title, main_keyword]):
        return Response(
            {'error': 'campaign_id, title و main_keyword الزامی هستند'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        campaign = Campaign.objects.get(id=campaign_id, workspace=workspace)

        with transaction.atomic():
            content_item = ContentItem.objects.create(
                campaign=campaign,
                title=title,
                main_keyword=main_keyword,
                additional_keywords=request.data.get('additional_keywords', []),
                description=request.data.get('description', ''),
                goal=request.data.get('goal', ''),
                platform=request.data.get('platform', 'website'),
                language=request.data.get('language', 'fa'),
                status='draft'
            )

            # ایجاد کلیدواژه اصلی
            Keyword.objects.create(
                content_item=content_item,
                keyword=main_keyword,
                source='user_input'
            )

        return Response({
            'content_item_id': content_item.id,
            'title': content_item.title,
            'status': content_item.status,
            'message': 'محتوا با موفقیت ایجاد شد'
        }, status=status.HTTP_201_CREATED)

    except Campaign.DoesNotExist:
        return Response(
            {'error': 'کمپین یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_content_item(request, content_id):
    """دریافت اطلاعات کامل یک ContentItem"""
    workspace = require_workspace_action(request, Actions.CONTENT_VIEW).workspace
    try:
        content_item = ContentItem.objects.select_related(
            'campaign'
        ).prefetch_related(
            'keywords',
            'research_sources'
        ).get(id=content_id, workspace=workspace)

        keywords = content_item.keywords.values(
            'id', 'keyword', 'source', 'is_selected'
        )

        research_sources = content_item.research_sources.values(
            'id', 'url', 'title', 'summary', 'created_at'
        )

        return Response({
            'id': content_item.id,
            'title': content_item.title,
            'main_keyword': content_item.main_keyword,
            'additional_keywords': content_item.additional_keywords,
            'description': content_item.description,
            'goal': content_item.goal,
            'platform': content_item.platform,
            'language': content_item.language,
            'status': content_item.status,
            'information': content_item.information,
            'campaign': {
                'id': content_item.campaign.id,
                'title': content_item.campaign.title
            },
            'keywords': list(keywords),
            'research_sources': list(research_sources),
            'created_at': content_item.created_at.isoformat(),
            'updated_at': content_item.updated_at.isoformat()
        }, status=status.HTTP_200_OK)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_content_item(request, content_id):
    """
    آپدیت ContentItem
    فیلدهای قابل ویرایش: title, main_keyword, additional_keywords,
    description, goal, platform, language, status, information
    """
    workspace = require_workspace_action(request, Actions.CONTENT_MUTATE).workspace
    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_id,
            workspace=workspace,
        )

        updatable_fields = {
            'title', 'main_keyword', 'additional_keywords',
            'description', 'goal', 'platform', 'language',
            'status', 'information'
        }

        updated_fields = []
        for field in updatable_fields:
            if field in request.data:
                setattr(content_item, field, request.data[field])
                updated_fields.append(field)

        if updated_fields:
            content_item.save(update_fields=updated_fields)

        return Response({
            'message': 'محتوا با موفقیت به‌روزرسانی شد',
            'updated_fields': updated_fields,
            'content_item': {
                'id': content_item.id,
                'title': content_item.title,
                'status': content_item.status
            }
        }, status=status.HTTP_200_OK)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_content_item(request, content_id):
    """حذف ContentItem و تمام موارد مرتبط"""
    workspace = require_workspace_action(request, Actions.CONTENT_DELETE).workspace
    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_id,
            workspace=workspace,
        )

        title = content_item.title
        content_item.delete()

        return Response({
            'message': f'محتوای "{title}" با موفقیت حذف شد'
        }, status=status.HTTP_200_OK)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_content_items(request):
    """لیست تمام محتواهای کاربر با فیلترهای مختلف"""
    campaign_id = request.query_params.get('campaign_id')
    status_filter = request.query_params.get('status')
    platform = request.query_params.get('platform')

    workspace = require_workspace_action(request, Actions.CONTENT_VIEW).workspace
    queryset = ContentItem.objects.filter(workspace=workspace).select_related('campaign')

    if campaign_id:
        queryset = queryset.filter(campaign_id=campaign_id)

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    if platform:
        queryset = queryset.filter(platform=platform)

    queryset = queryset.order_by('-created_at')

    items = queryset.values(
        'id', 'title', 'main_keyword', 'platform',
        'status', 'language', 'created_at',
        'campaign__id', 'campaign__title'
    )

    items_data = [
        {
            'id': item['id'],
            'title': item['title'],
            'main_keyword': item['main_keyword'],
            'platform': item['platform'],
            'status': item['status'],
            'language': item['language'],
            'created_at': item['created_at'].isoformat(),
            'campaign': {
                'id': item['campaign__id'],
                'title': item['campaign__title']
            }
        }
        for item in items
    ]

    return Response({
        'count': len(items_data),
        'items': items_data
    }, status=status.HTTP_200_OK)


# ============================================================
# Keywords Management - مدیریت کلیدواژه‌ها
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_keyword(request):
    """ساخت کلیدواژه تکی"""
    content_item_id = request.data.get('content_item_id')
    keyword_text = request.data.get('keyword', '').strip()
    source = request.data.get('source', 'user_input')

    if not all([content_item_id, keyword_text]):
        return Response(
            {'error': 'content_item_id و keyword الزامی هستند'},
            status=status.HTTP_400_BAD_REQUEST
        )

    workspace = require_workspace_action(request, Actions.CONTENT_MUTATE).workspace
    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_item_id,
            workspace=workspace,
        )

        # بررسی تکراری نبودن
        if Keyword.objects.filter(
                content_item=content_item,
                keyword__iexact=keyword_text
        ).exists():
            return Response(
                {'error': 'این کلیدواژه قبلاً اضافه شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        keyword = Keyword.objects.create(
            content_item=content_item,
            keyword=keyword_text,
            source=source
        )

        return Response({
            'id': keyword.id,
            'keyword': keyword.keyword,
            'source': keyword.source,
            'is_selected': keyword.is_selected,
            'message': 'کلیدواژه با موفقیت اضافه شد'
        }, status=status.HTTP_201_CREATED)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_keywords(request):
    """ساخت دسته‌ای کلیدواژه‌ها"""
    content_item_id = request.data.get('content_item_id')
    keywords_list = request.data.get('keywords', [])

    if not content_item_id:
        return Response(
            {'error': 'content_item_id الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(keywords_list, list) or not keywords_list:
        return Response(
            {'error': 'لیست کلیدواژه‌ها نامعتبر است'},
            status=status.HTTP_400_BAD_REQUEST
        )

    workspace = require_workspace_action(request, Actions.CONTENT_MUTATE).workspace
    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_item_id,
            workspace=workspace,
        )

        # دریافت کلیدواژه‌های موجود
        existing_keywords = set(
            Keyword.objects.filter(content_item=content_item)
            .values_list('keyword', flat=True)
        )

        keyword_objects = []
        skipped = []

        for item in keywords_list:
            if not isinstance(item, dict):
                continue

            keyword_text = item.get('keyword', '').strip()
            source = item.get('source', 'ai_generated')

            if not keyword_text:
                continue

            # بررسی تکراری
            if keyword_text.lower() in [k.lower() for k in existing_keywords]:
                skipped.append(keyword_text)
                continue

            keyword_objects.append(
                Keyword(
                    content_item=content_item,
                    keyword=keyword_text,
                    source=source
                )
            )
            existing_keywords.add(keyword_text)

        if keyword_objects:
            created_keywords = Keyword.objects.bulk_create(keyword_objects)

            return Response({
                'created_count': len(created_keywords),
                'skipped_count': len(skipped),
                'skipped': skipped,
                'keywords': [
                    {
                        'id': kw.id,
                        'keyword': kw.keyword,
                        'source': kw.source
                    }
                    for kw in created_keywords
                ],
                'message': f'{len(created_keywords)} کلیدواژه با موفقیت اضافه شد'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'هیچ کلیدواژه معتبری برای افزودن وجود ندارد'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_keyword(request, keyword_id):
    """آپدیت کلیدواژه"""
    workspace = require_workspace_action(request, Actions.CONTENT_MUTATE).workspace
    try:
        keyword = Keyword.objects.select_related(
            'content_item__campaign'
        ).get(
            id=keyword_id,
            content_item__workspace=workspace,
        )

        updatable_fields = {'keyword', 'source', 'is_selected'}
        updated_fields = []

        for field in updatable_fields:
            if field in request.data:
                setattr(keyword, field, request.data[field])
                updated_fields.append(field)

        if updated_fields:
            keyword.save(update_fields=updated_fields)

        return Response({
            'id': keyword.id,
            'keyword': keyword.keyword,
            'source': keyword.source,
            'is_selected': keyword.is_selected,
            'message': 'کلیدواژه به‌روزرسانی شد'
        }, status=status.HTTP_200_OK)

    except Keyword.DoesNotExist:
        return Response(
            {'error': 'کلیدواژه یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_keyword(request, keyword_id):
    """حذف کلیدواژه"""
    workspace = require_workspace_action(request, Actions.CONTENT_DELETE).workspace
    try:
        keyword = Keyword.objects.select_related(
            'content_item__campaign'
        ).get(
            id=keyword_id,
            content_item__workspace=workspace,
        )

        keyword_text = keyword.keyword
        keyword.delete()

        return Response({
            'message': f'کلیدواژه "{keyword_text}" حذف شد'
        }, status=status.HTTP_200_OK)

    except Keyword.DoesNotExist:
        return Response(
            {'error': 'کلیدواژه یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_keywords(request, content_id):
    """لیست کلیدواژه‌های یک محتوا"""
    workspace = require_workspace_action(request, Actions.CONTENT_VIEW).workspace
    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_id,
            workspace=workspace,
        )

        keywords = Keyword.objects.filter(
            content_item=content_item
        ).order_by('-created_at').values(
            'id', 'keyword', 'source', 'is_selected', 'created_at'
        )

        return Response({
            'content_item_id': content_item.id,
            'count': len(keywords),
            'keywords': list(keywords)
        }, status=status.HTTP_200_OK)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


# ============================================================
# AI Generation Pipeline - تولید محتوا با AI
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_keywords_ai(request):
    """تولید کلیدواژه با AI"""
    workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
    content_id = request.data.get('content_id')

    if not content_id:
        return Response(
            {'error': 'content_id الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_id,
            workspace=workspace,
        )

        # استفاده از سرویس AI برای تولید کلیدواژه
        prompt_service = PromptService()
        ai_service = AITextService()

        # ساخت prompt
        prompt = prompt_service.build_keyword_generation_prompt(
            main_keyword=content_item.main_keyword,
            description=content_item.description,
            platform=content_item.platform,
            language=content_item.language
        )

        # فراخوانی AI
        ai_response = ai_service.generate_text(prompt)

        # پارس کردن کلیدواژه‌ها از پاسخ AI
        keywords_data = prompt_service.parse_keywords_response(ai_response)

        # ذخیره کلیدواژه‌های جدید
        existing_keywords = set(
            Keyword.objects.filter(content_item=content_item)
            .values_list('keyword', flat=True)
        )

        keyword_objects = []
        for kw_text in keywords_data:
            if kw_text.lower() not in [k.lower() for k in existing_keywords]:
                keyword_objects.append(
                    Keyword(
                        content_item=content_item,
                        keyword=kw_text,
                        source='ai_generated'
                    )
                )

        if keyword_objects:
            created_keywords = Keyword.objects.bulk_create(keyword_objects)

            return Response({
                'content_item_id': content_item.id,
                'generated_count': len(created_keywords),
                'keywords': [
                    {
                        'id': kw.id,
                        'keyword': kw.keyword,
                        'source': kw.source
                    }
                    for kw in created_keywords
                ],
                'message': f'{len(created_keywords)} کلیدواژه با AI تولید شد'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'همه کلیدواژه‌های پیشنهادی قبلاً وجود داشتند',
                'generated_count': 0
            }, status=status.HTTP_200_OK)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'خطا در تولید کلیدواژه: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class GenerateOutlineAPI(APIView):
    """
    تولید طرح کلی (Outline) محتوا
    Mock implementation - باید با سرویس واقعی جایگزین شود
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
        content_id = request.data.get('content_id')

        if not content_id:
            return Response(
                {'error': 'content_id الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_item = ContentItem.objects.select_related('campaign').get(
                id=content_id,
                workspace=workspace,
            )

            # Mock outline - در نسخه واقعی باید از AI استفاده شود
            outline = {
                'title': content_item.title,
                'sections': [
                    {
                        'heading': 'مقدمه',
                        'description': 'معرفی موضوع و اهمیت آن',
                        'keywords': [content_item.main_keyword]
                    },
                    {
                        'heading': 'بخش اصلی',
                        'description': 'توضیحات تفصیلی',
                        'keywords': content_item.additional_keywords[:3]
                    },
                    {
                        'heading': 'نتیجه‌گیری',
                        'description': 'خلاصه و جمع‌بندی',
                        'keywords': []
                    }
                ]
            }

            # ذخیره outline در information
            if not content_item.information:
                content_item.information = {}

            content_item.information['outline'] = outline
            content_item.save(update_fields=['information'])

            return Response({
                'content_item_id': content_item.id,
                'outline': outline,
                'message': 'طرح کلی با موفقیت تولید شد'
            }, status=status.HTTP_200_OK)

        except ContentItem.DoesNotExist:
            return Response(
                {'error': 'محتوا یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )


class GenerateFinalContentAPI(APIView):
    """
    تولید محتوای نهایی با استفاده از AI
    شامل مدیریت وضعیت و ذخیره نتیجه
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = require_workspace_action(request, Actions.CONTENT_DRAFT).workspace
        content_id = request.data.get('content_id')

        if not content_id:
            return Response(
                {'error': 'content_id الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_item = ContentItem.objects.select_related('campaign').get(
                id=content_id,
                workspace=workspace,
            )

            # تغییر وضعیت به generating
            content_item.status = 'generating'
            content_item.save(update_fields=['status'])

            try:
                # استفاده از سرویس‌های AI
                prompt_service = PromptService()
                ai_service = AITextService()

                # دریافت کلیدواژه‌ها
                keywords = list(
                    Keyword.objects.filter(content_item=content_item)
                    .values_list('keyword', flat=True)
                )

                # دریافت منابع تحقیق
                research_sources = list(
                    ResearchSource.objects.filter(content_item=content_item)
                    .values('url', 'title', 'summary')
                )

                # ساخت prompt
                prompt = prompt_service.build_content_generation_prompt(
                    title=content_item.title,
                    main_keyword=content_item.main_keyword,
                    keywords=keywords,
                    description=content_item.description,
                    goal=content_item.goal,
                    platform=content_item.platform,
                    language=content_item.language,
                    outline=content_item.information.get('outline') if content_item.information else None,
                    research_sources=research_sources
                )

                # تولید محتوا
                generated_content = ai_service.generate_text(prompt)

                # ذخیره محتوای تولید شده
                if not content_item.information:
                    content_item.information = {}

                content_item.information['generated_content'] = generated_content
                content_item.information['generation_timestamp'] = str(
                    timezone.now().isoformat()
                )
                content_item.status = 'completed'
                content_item.save(update_fields=['information', 'status'])

                return Response({
                    'content_item_id': content_item.id,
                    'status': 'completed',
                    'content': generated_content,
                    'word_count': len(generated_content.split()),
                    'message': 'محتوا با موفقیت تولید شد'
                }, status=status.HTTP_200_OK)

            except Exception as generation_error:
                # در صورت خطا، وضعیت را به draft برگردان
                content_item.status = 'draft'
                content_item.save(update_fields=['status'])
                raise generation_error

        except ContentItem.DoesNotExist:
            return Response(
                {'error': 'محتوا یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'خطا در تولید محتوا: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# Research Sources - مدیریت منابع تحقیق
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_research_source_to_content(request):
    """افزودن منبع تحقیق به ContentItem"""
    workspace = require_workspace_action(request, Actions.CONTENT_MUTATE).workspace
    content_id = request.data.get('content_id')
    url = request.data.get('url', '').strip()
    title = request.data.get('title', '').strip()
    summary = request.data.get('summary', '').strip()

    if not all([content_id, url]):
        return Response(
            {'error': 'content_id و url الزامی هستند'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        content_item = ContentItem.objects.select_related('campaign').get(
            id=content_id,
            workspace=workspace,
        )

        # بررسی تکراری نبودن URL
        if ResearchSource.objects.filter(
            content_item=content_item,
            url=url
        ).exists():
            return Response(
                {'error': 'این منبع قبلاً اضافه شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        research_source = ResearchSource.objects.create(
            content_item=content_item,
            url=url,
            title=title or url,
            summary=summary
        )

        return Response({
            'id': research_source.id,
            'url': research_source.url,
            'title': research_source.title,
            'summary': research_source.summary,
            'created_at': research_source.created_at.isoformat(),
            'message': 'منبع تحقیق با موفقیت اضافه شد'
        }, status=status.HTTP_201_CREATED)

    except ContentItem.DoesNotExist:
        return Response(
            {'error': 'محتوا یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )


