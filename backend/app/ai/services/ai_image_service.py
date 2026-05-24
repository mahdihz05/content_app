from ai.clients.ai_client import AIClient


class AIImageService:
    def __init__(self):
        self.client = AIClient()

    def generate(self, prompt: str, size: str = "1024x1024") -> str:
        """تولید تصویر و برگرداندن URL"""
        return self.client.generate_image(prompt=prompt, size=size)
