from rest_framework.views import APIView
from rest_framework.response import Response

from messaging_automation.ai.ai_client import AIClient


class AIChatAPIView(APIView):

    def post(self, request):

        text = request.data.get("message")

        ai = AIClient(
            api_key="YOUR_OPENAI_KEY"
        )

        response = ai.generate_reply(text)

        return Response({
            "response": response
        })