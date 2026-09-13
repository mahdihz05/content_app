from openai import OpenAI
from django.conf import settings


class AIClient:

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.AI_API_KEY,
                base_url="https://api.gapgpt.app/v1"
            )
        return self._client

    # --------------------
    # TEXT
    # --------------------

    def chat(self, messages, model="gapgpt-qwen-3.5", temperature=0.3):

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

        return response.choices[0].message.content


    # --------------------
    # IMAGE
    # --------------------
    def generate_image(self, prompt, model="gemini-2.5-flash-image", size="1024x1024"):
        import base64, os, uuid
        from django.conf import settings

        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size
        )

        image_data = response.data[0]

        # اگر URL مستقیم داشت، همون رو برگردون
        if image_data.url:
            return image_data.url

        # اگر base64 بود، ذخیره کن و URL محلی برگردون
        if image_data.b64_json:
            media_root = settings.MEDIA_ROOT
            save_dir = os.path.join(media_root, "ai_images")
            os.makedirs(save_dir, exist_ok=True)

            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_data.b64_json))

            return f"{settings.MEDIA_URL}ai_images/{filename}"

        raise ValueError("API response contains neither URL nor base64 image data")

    # --------------------
    # SPEECH TO TEXT
    # --------------------

    def transcribe_audio(self, audio_file, model="whisper-1"):

        response = self.client.audio.transcriptions.create(
            file=audio_file,
            model=model
        )

        return response.text


    # --------------------
    # TEXT TO SPEECH
    # --------------------

    def generate_speech(self, text, voice="alloy", model="gpt-4o-mini-tts"):

        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        return response
