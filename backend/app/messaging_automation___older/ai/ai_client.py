from openai import OpenAI


class AIClient:

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_reply(self, text):

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        return response.choices[0].message.content