from ai.clients.ai_client import AIClient


class AIAudioService:

    def __init__(self):
        self.client = AIClient()

    def speech_to_text(self, audio_file):

        return self.client.transcribe_audio(audio_file)


    def text_to_speech(self, text):

        return self.client.generate_speech(text)
