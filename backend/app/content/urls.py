from django.urls import path

from content.views.ai_chat import (
    # =========================================================
    # AI Chat
    # =========================================================
    AIStartSession,
    AISendMessage,
    AIGenerateImage,
    AISessionHistory,
    AINewConversation,

    # =========================================================
    # Content CRUD
    # =========================================================
    create_content_item,
    get_content_item,
    update_content_item,
    delete_content_item,
    list_content_items,

    # =========================================================
    # Keywords
    # =========================================================
    create_keyword,
    bulk_create_keywords,
    update_keyword,
    delete_keyword,
    list_keywords,

    # =========================================================
    # AI Generation
    # =========================================================
    generate_keywords_ai,
    GenerateOutlineAPI,
    GenerateFinalContentAPI,

    # =========================================================
    # Research Sources
    # =========================================================
    add_research_source_to_content,
)

app_name = 'content'

urlpatterns = [

    # =========================================================
    # AI Chat Interface
    # =========================================================

    # صفحه اصلی رابط چت
    path(
        'ai/chat/',
        AIStartSession.as_view(),
        name='ai_chat_page'
    ),

    # ارسال پیام به AI
    path(
        'api/v1/ai/chat/send/',
        AISendMessage.as_view(),
        name='ai_send_message'
    ),

    # تولید تصویر
    path(
        'api/v1/ai/chat/generate-image/',
        AIGenerateImage.as_view(),
        name='ai_generate_image'
    ),

    # شروع مکالمه جدید
    path(
        'api/v1/ai/chat/new/',
        AINewConversation.as_view(),
        name='ai_new_conversation'
    ),

    # تاریخچه سشن
    path(
        'api/v1/ai/chat/sessions/<int:session_id>/',
        AISessionHistory.as_view(),
        name='ai_session_history'
    ),

    # =========================================================
    # Content Items
    # =========================================================

    # ساخت محتوا
    path(
        'api/v1/content/',
        create_content_item,
        name='create_content_item'
    ),

    # لیست محتواها
    path(
        'api/v1/content/list/',
        list_content_items,
        name='list_content_items'
    ),

    # جزئیات محتوا
    path(
        'api/v1/content/<int:content_id>/',
        get_content_item,
        name='get_content_item'
    ),

    # ویرایش محتوا
    path(
        'api/v1/content/<int:content_id>/update/',
        update_content_item,
        name='update_content_item'
    ),

    # حذف محتوا
    path(
        'api/v1/content/<int:content_id>/delete/',
        delete_content_item,
        name='delete_content_item'
    ),

    # =========================================================
    # Keywords
    # =========================================================

    # ساخت کلیدواژه
    path(
        'api/v1/keywords/',
        create_keyword,
        name='create_keyword'
    ),

    # ساخت دسته‌ای
    path(
        'api/v1/keywords/bulk/',
        bulk_create_keywords,
        name='bulk_create_keywords'
    ),

    # لیست کلیدواژه‌های محتوا
    path(
        'api/v1/content/<int:content_id>/keywords/',
        list_keywords,
        name='list_keywords'
    ),

    # ویرایش کلیدواژه
    path(
        'api/v1/keywords/<int:keyword_id>/update/',
        update_keyword,
        name='update_keyword'
    ),

    # حذف کلیدواژه
    path(
        'api/v1/keywords/<int:keyword_id>/delete/',
        delete_keyword,
        name='delete_keyword'
    ),

    # =========================================================
    # AI Generation Pipeline
    # =========================================================

    # تولید کلیدواژه با AI
    path(
        'api/v1/ai/generate-keywords/',
        generate_keywords_ai,
        name='generate_keywords_ai'
    ),

    # تولید Outline
    path(
        'api/v1/ai/generate-outline/',
        GenerateOutlineAPI.as_view(),
        name='generate_outline'
    ),

    # تولید محتوای نهایی
    path(
        'api/v1/ai/generate-content/',
        GenerateFinalContentAPI.as_view(),
        name='generate_final_content'
    ),

    # =========================================================
    # Research Sources
    # =========================================================

    # افزودن سورس تحقیق
    path(
        'api/v1/content/<int:content_id>/sources/',
        add_research_source_to_content,
        name='add_research_source'
    ),
]