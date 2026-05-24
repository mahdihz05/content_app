# ai/services/entity_extractor.py
from typing import Dict, Optional, List
from .ai_text_service import AITextService


class EntityExtractor:
    """
    استخراج اطلاعات ساختاریافته از متن طبیعی کاربر
    """

    def __init__(self):
        self.text_service = AITextService()

    def extract(self, user_message: str, current_data: Dict = None) -> Dict:
        """
        استخراج اطلاعات از پیام کاربر (متد اصلی که orchestrator صدا می‌زنه)

        Returns:
        {
            'title': str or None,
            'description': str or None,
            'platform': str or None,
            'keywords': list or None,
            'topic': str or None,
            'tone': str or None,
            'target_audience': str or None
        }
        """
        return self.extract_content_info(user_message, current_data)

    def extract_content_info(
            self,
            user_message: str,
            current_data: Dict = None
    ) -> Dict:
        """
        استخراج اطلاعات محتوا از پیام کاربر

        Returns:
        {
            'title': str or None,
            'description': str or None,
            'platform': str or None,
            'keywords': list or None,
            'topic': str or None,
            'tone': str or None,
            'target_audience': str or None
        }
        """
        current_data = current_data or {}

        prompt = f"""
از متن زیر، اطلاعات مربوط به محتوای بازاریابی را استخراج کن:

متن کاربر: "{user_message}"

اطلاعات فعلی:
{self._format_current_data(current_data)}

لطفاً در قالب زیر پاسخ بده (اگر اطلاعاتی در متن نیست، همان مقدار فعلی را بنویس یا NONE):

TITLE: [عنوان محتوا]
DESCRIPTION: [توضیحات محتوا]
PLATFORM: [instagram/telegram/linkedin/twitter یا NONE]
KEYWORDS: [کلمه1, کلمه2, ... یا NONE]
TOPIC: [موضوع اصلی]
TONE: [formal/friendly/professional/casual/humorous یا NONE]
TARGET_AUDIENCE: [مخاطب هدف یا NONE]

فقط همین فرمت را برگردان، بدون توضیح اضافی.
"""

        response = self.text_service.chat([
            {"role": "system", "content": "شما یک استخراج‌کننده اطلاعات هستید. فقط در قالب خواسته شده پاسخ دهید."},
            {"role": "user", "content": prompt}
        ], temperature=0.2)

        return self._parse_extraction(response, current_data)

    def _format_current_data(self, data: Dict) -> str:
        """فرمت کردن داده‌های فعلی برای نمایش"""
        lines = []
        if data.get('title'):
            lines.append(f"عنوان فعلی: {data['title']}")
        if data.get('description'):
            lines.append(f"توضیحات فعلی: {data['description']}")
        if data.get('platform'):
            lines.append(f"پلتفرم فعلی: {data['platform']}")
        if data.get('keywords'):
            lines.append(f"کلمات کلیدی فعلی: {', '.join(data['keywords'])}")
        if data.get('topic'):
            lines.append(f"موضوع فعلی: {data['topic']}")
        if data.get('tone'):
            lines.append(f"لحن فعلی: {data['tone']}")
        if data.get('target_audience'):
            lines.append(f"مخاطب فعلی: {data['target_audience']}")

        return '\n'.join(lines) if lines else "هیچ اطلاعاتی ثبت نشده"

    def _parse_extraction(self, response: str, current_data: Dict) -> Dict:
        """پارس کردن خروجی LLM"""
        result = {
            'title': current_data.get('title'),
            'description': current_data.get('description'),
            'platform': current_data.get('platform'),
            'keywords': current_data.get('keywords', []),
            'topic': current_data.get('topic'),
            'tone': current_data.get('tone'),
            'target_audience': current_data.get('target_audience')
        }

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                value = line.replace('TITLE:', '').strip()
                if value and value != 'NONE':
                    result['title'] = value

            elif line.startswith('DESCRIPTION:'):
                value = line.replace('DESCRIPTION:', '').strip()
                if value and value != 'NONE':
                    result['description'] = value

            elif line.startswith('PLATFORM:'):
                value = line.replace('PLATFORM:', '').strip().lower()
                if value in ['instagram', 'telegram', 'linkedin', 'twitter']:
                    result['platform'] = value

            elif line.startswith('KEYWORDS:'):
                value = line.replace('KEYWORDS:', '').strip()
                if value and value != 'NONE':
                    keywords = [k.strip() for k in value.split(',')]
                    result['keywords'] = [k for k in keywords if k]

            elif line.startswith('TOPIC:'):
                value = line.replace('TOPIC:', '').strip()
                if value and value != 'NONE':
                    result['topic'] = value

            elif line.startswith('TONE:'):
                value = line.replace('TONE:', '').strip().lower()
                if value in ['formal', 'friendly', 'professional', 'casual', 'humorous']:
                    result['tone'] = value

            elif line.startswith('TARGET_AUDIENCE:'):
                value = line.replace('TARGET_AUDIENCE:', '').strip()
                if value and value != 'NONE':
                    result['target_audience'] = value

        return result
