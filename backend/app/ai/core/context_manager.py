# ai/core/context_manager.py

class ContextManager:

    def get_user_context(self, user):
        """
        اینجا می‌تواند:
        - زبان کاربر
        - برند
        - tone
        - اهداف
        را برگرداند.
        """

        return {
            "language": "fa",
            "tone": "friendly",
            "brand_voice": getattr(user, "brand_voice", None),
        }
