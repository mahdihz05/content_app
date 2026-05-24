from ai.services.ai_text_service import AITextService
from ai.services.embedding_service import EmbeddingService
from ai.services.ai_image_service import AIImageService  # اضافه کن


class AIBrain:
    def __init__(self):
        self.text = AITextService()
        self.embed = EmbeddingService()
        self.image = AIImageService()  # اضافه کن

    def llm(self, system_prompt, user_prompt, model="gpt-4.1-mini"):
        return self.text.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model
        )

    def embeddings(self, input_text):
        return self.embed.generate_embedding(input_text)

    def generate_image(self, prompt: str, size: str = "1024x1024") -> str:
        return self.image.generate(prompt=prompt, size=size)
