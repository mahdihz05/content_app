# views.py
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST
from ai.services.ai_service import AIService


# صفحه لندینگ
def landing_view(request):
    return render(request, "landing.html")


# پرامپت سیستم
LANDING_CHAT_SYSTEM_PROMPT = """
You are the AI Content Platform Landing Chatbot.

ROLE:
- You are the assistant for a SaaS platform that automates content research and generation using Django + n8n + LLMs.
- You help visitors understand how the platform works (research, outline, generation, SEO, etc.).
- You can also simulate how the real system would think about keyword research, campaign planning, and content outlines.

RULES:
- Answer in Persian (Farsi).
- Be concise, practical, and clear.
- Avoid long texts.
- If the user seems interested in the product suggest creating a campaign or signing up.
- You cannot claim you run real scraping or Google search here. You are only a simulator.
- Respond with normal Persian text only.
"""


@require_POST
def landing_chat_api(request):

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    user_message = data.get("message", "").strip()

    if not user_message:
        return HttpResponseBadRequest("Empty message")

    try:

        messages = [
            {"role": "system", "content": LANDING_CHAT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        reply = AIService().chat(
            messages=messages,
            temperature=0.6,
            max_tokens=500
        )

    except Exception:
        reply = "در پردازش درخواست مشکلی پیش آمد. لطفاً چند لحظه بعد دوباره تلاش کنید."

    return JsonResponse({
        "reply": reply
    })
