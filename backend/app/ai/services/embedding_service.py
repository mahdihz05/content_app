# ai/services/embedding_service.py

from ai.clients.ai_client import AIClient


class EmbeddingService:

    def __init__(self):
        self.client = AIClient()

    def generate_embedding(self, text):
        return self.client.embedding(text)
