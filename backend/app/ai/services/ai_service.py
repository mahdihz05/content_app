# ai/services/ai_service.py

import json
import re

from typing import Dict, List, Optional, Any

from .ai_text_service import AITextService
from .ai_image_service import AIImageService


class AIService:

    ALLOWED_ACTIONS = {
        "UPDATE_CONTENT_ITEM",
        "CREATE_CONTENT_ITEM",
        "UPDATE_CONTENT_DETAILS",
        "UPDATE_PLATFORM",
        "UPDATE_GOAL",
        "STATE_NEXT",
        "STATE_BACK",
        "SHOW_SELECT_BUTTONS",
        "START_RESEARCH",
        "GENERATE_RESEARCH",
        "SKIP_RESEARCH",
        "GENERATE_CONTENT",
    }

    ALLOWED_FIELDS = {
        "platform",
        "goal",
        "title",
        "main_keyword",
        "keywords",
        "tone",
        "target_audience",
        "length",
    }

    def __init__(self):
        self.text_service = AITextService()
        self.image_service = AIImageService()

    # =========================================================
    # MAIN CHAT
    # =========================================================

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: str = "text"
    ) -> str:

        if response_format == "json":
            return self._chat_json(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

        return self.text_service.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    # =========================================================
    # JSON CHAT
    # =========================================================

    def _chat_json(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: Optional[int]
    ) -> str:

        modified_messages = self._prepare_json_messages(messages)

        response = self.text_service.chat(
            messages=modified_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        print("\n========== AI RAW RESPONSE ==========")
        print(response)
        print("=====================================\n")

        extracted = self._extract_json(response)

        try:
            parsed = json.loads(extracted)

            # اگر مدل آرایه برگرداند
            if isinstance(parsed, list):

                if len(parsed) > 0 and isinstance(parsed[0], dict):
                    parsed = parsed[0]
                else:
                    parsed = {}

            # اگر هنوز dict نبود
            if not isinstance(parsed, dict):
                parsed = {}

            # نرمال‌سازی
            parsed["message"] = str(
                parsed.get("message", "")
            )

            orders = parsed.get("orders", [])

            if not isinstance(orders, list):
                orders = []

            quick_replies = parsed.get("quick_replies", [])

            if not isinstance(quick_replies, list):
                quick_replies = []

            parsed["orders"] = orders
            parsed["quick_replies"] = quick_replies

            print("\n========== AI NORMALIZED RESPONSE ==========")
            print(
                json.dumps(
                    parsed,
                    indent=2,
                    ensure_ascii=False
                )
            )
            print("============================================\n")

            return json.dumps(
                parsed,
                ensure_ascii=False
            )

        except Exception as e:

            print(f"\n❌ JSON PARSE ERROR: {e}\n")

            fallback = {
                "message": response,
                "orders": [],
                "quick_replies": []
            }

            return json.dumps(
                fallback,
                ensure_ascii=False
            )

    # =========================================================
    # PREPARE JSON PROMPT
    # =========================================================

    def _prepare_json_messages(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:

        modified = []

        for msg in messages:
            modified.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })

        json_instruction = """
IMPORTANT RULES:

You MUST respond ONLY with valid JSON.

DO NOT:
- write markdown
- write explanation
- use ```json
- add text before JSON
- add text after JSON

VALID RESPONSE FORMAT:

{
  "message": "text",
  "orders": [],
  "quick_replies": []
}

RULES:
- orders must always be array
- quick_replies must always be array
- action names must be uppercase
- invalid actions are forbidden
"""

        system_found = False

        for msg in modified:

            if msg["role"] == "system":
                msg["content"] += "\n\n" + json_instruction
                system_found = True
                break

        if not system_found:
            modified.insert(0, {
                "role": "system",
                "content": json_instruction
            })

        return modified

    # =========================================================
    # JSON EXTRACTION
    # =========================================================

    def _extract_json(self, text: str) -> str:

        if not text:
            return "{}"

        text = text.strip()

        # remove markdown blocks
        text = re.sub(r"^```json", "", text)
        text = re.sub(r"^```", "", text)
        text = re.sub(r"```$", "", text)

        text = text.strip()

        if text.startswith("{") and text.endswith("}"):
            return text

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            return match.group(0)

        return "{}"

    # =========================================================
    # SAFE PARSE
    # =========================================================

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:

        try:
            parsed = json.loads(text)

            if not isinstance(parsed, dict):
                raise ValueError("response must be object")

            return parsed

        except Exception as e:

            print(f"❌ JSON parse error: {e}")

            return {
                "message": "متوجه شدم. لطفاً کمی واضح‌تر توضیح بده.",
                "orders": [],
                "quick_replies": [],
            }

    # =========================================================
    # NORMALIZATION
    # =========================================================

    def _normalize_response(
        self,
        parsed: Dict[str, Any]
    ) -> Dict[str, Any]:

        parsed.setdefault("message", "")
        parsed.setdefault("orders", [])
        parsed.setdefault("quick_replies", [])

        if not isinstance(parsed["orders"], list):
            parsed["orders"] = []

        if not isinstance(parsed["quick_replies"], list):
            parsed["quick_replies"] = []

        parsed["orders"] = self._normalize_orders(
            parsed["orders"]
        )

        parsed["quick_replies"] = self._normalize_quick_replies(
            parsed["quick_replies"]
        )

        return parsed

    # =========================================================
    # NORMALIZE ORDERS
    # =========================================================

    def _normalize_orders(
        self,
        orders: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        normalized = []

        for order in orders:

            if not isinstance(order, dict):
                continue

            action = str(
                order.get("action", "")
            ).upper().strip()

            if action not in self.ALLOWED_ACTIONS:
                print(f"⚠️ Invalid action skipped: {action}")
                continue

            clean_order = {
                "action": action
            }

            if "field" in order:
                field = str(order["field"]).strip()

                if field in self.ALLOWED_FIELDS:
                    clean_order["field"] = field

            if "value" in order:
                clean_order["value"] = order["value"]

            if "data" in order and isinstance(order["data"], dict):
                clean_order["data"] = order["data"]

            if "options" in order:
                clean_order["options"] = order["options"]

            normalized.append(clean_order)

        return normalized

    # =========================================================
    # QUICK REPLIES
    # =========================================================

    def _normalize_quick_replies(
        self,
        quick_replies: List[Any]
    ) -> List[Dict[str, str]]:

        normalized = []

        for item in quick_replies:

            if isinstance(item, str):

                normalized.append({
                    "label": item,
                    "value": item
                })

            elif isinstance(item, dict):

                label = str(
                    item.get("label", "")
                ).strip()

                value = str(
                    item.get("value", label)
                ).strip()

                if label:
                    normalized.append({
                        "label": label,
                        "value": value
                    })

        return normalized[:8]

    # =========================================================
    # RESEARCH
    # =========================================================

    def generate_research(
        self,
        topic: str,
        keywords: List[str]
    ) -> str:

        prompt = f"""
موضوع:
{topic}

کلمات کلیدی:
{", ".join(keywords)}

تحلیل کامل تولید کن شامل:
- دغدغه مخاطب
- سوالات پرتکرار
- ترندها
- ایده‌های وایرال
- CTA های موثر
- پیشنهاد زاویه محتوا
"""

        return self.text_service.chat(
            [
                {
                    "role": "system",
                    "content": "شما متخصص تحقیق بازار و تحلیل محتوا هستید."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

    # =========================================================
    # ARTICLE GENERATION
    # =========================================================

    def generate_article(
        self,
        title: str,
        description: str,
        research: str,
        platform: str,
        keywords: List[str]
    ) -> str:

        keywords_text = ", ".join(keywords)

        prompt = f"""
موضوع محتوا:
{title}

اطلاعات:
{description}

پلتفرم:
{platform}

کلمات کلیدی:
{keywords_text}

تحقیقات:
{research}

قوانین تولید محتوا:

- محتوا باید کاملاً انسانی باشد
- کلی‌گویی ممنوع
- CTA واقعی داشته باشد
- محتوای زرد تولید نکن
- از متن‌های تکراری AI دوری کن
- Hook قوی در ابتدای محتوا بنویس
- ساختار خوانا داشته باش
- متناسب با پلتفرم بنویس
- اگر پلتفرم اینستاگرام بود:
  - کوتاه‌تر
  - جذاب‌تر
  - دارای hook
  - دارای CTA
  - دارای هشتگ
- اگر لینکدین بود:
  - حرفه‌ای
  - تحلیلی
  - دارای insight
- اگر توییتر بود:
  - کوتاه
  - punchy
  - thread style

خروجی نهایی فقط خود محتوا باشد.
"""

        return self.text_service.chat(
            [
                {
                    "role": "system",
                    "content": (
                        f"شما متخصص حرفه‌ای تولید محتوای {platform} هستید."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

    # =========================================================
    # KEYWORDS
    # =========================================================

    def generate_keywords(
        self,
        topic: str,
        platform: str
    ) -> List[str]:

        prompt = f"""
برای موضوع "{topic}" در پلتفرم "{platform}"

فقط 5 کلمه کلیدی مهم تولید کن.

خروجی فقط comma separated باشد.
"""

        response = self.text_service.chat(
            [
                {
                    "role": "system",
                    "content": "شما متخصص SEO هستید."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        keywords = [
            k.strip()
            for k in response.split(",")
            if k.strip()
        ]

        return keywords[:5]

    # =========================================================
    # IMAGE
    # =========================================================

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024"
    ) -> str:

        return self.image_service.generate(
            prompt=prompt,
            size=size
        )