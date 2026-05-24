# ai/services/ai_text_service.py

import json
import openai

from django.conf import settings
from typing import List, Dict, Optional


class AITextService:
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=getattr(
                settings,
                'OPENAI_BASE_URL',
                'https://api.gapgpt.app/v1'
            ),
            api_key=settings.OPENAI_API_KEY
        )

        self.model = getattr(
            settings,
            'OPENAI_MODEL',
            'gpt-4.1-mini'
        )

    def chat(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: Optional[int] = None
    ) -> str:
        """
        ارسال پیام به مدل
        """

        try:
            cleaned_messages = self._sanitize_messages(messages)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=cleaned_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=120
            )

            content = response.choices[0].message.content

            if not content:
                return ""

            return content.strip()

        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")

    def chat_with_history(
            self,
            system_prompt: str,
            user_message: str,
            history: Optional[List[Dict[str, str]]] = None,
            temperature: float = 0.7
    ) -> str:
        """
        چت با history
        """

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        if history:
            messages.extend(history)

        messages.append({
            "role": "user",
            "content": user_message
        })

        return self.chat(
            messages=messages,
            temperature=temperature
        )

    def _sanitize_messages(
            self,
            messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        پاکسازی message ها قبل از ارسال
        """

        cleaned = []

        for msg in messages:

            role = msg.get("role")
            content = msg.get("content")

            if not role or not content:
                continue

            cleaned.append({
                "role": str(role),
                "content": str(content)
            })

        return cleaned