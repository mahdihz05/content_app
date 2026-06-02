from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from messaging_automation.models.telegram_bot import TelegramBot
from messaging_automation.services.telegram_api import TelegramAPI


class RegisterTelegramBotAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        token = request.data.get("bot_token")

        if not token:

            return Response({
                "success": False,
                "error": "bot_token required"
            }, status=400)

        api = TelegramAPI(token)

        me = api.get_me()

        if not me.get("ok"):

            return Response({
                "success": False,
                "error": "invalid token"
            }, status=400)

        result = me.get("result")

        bot = TelegramBot.objects.create(
            user=request.user,
            name=result.get("first_name"),
            bot_token=token,
            bot_username=result.get("username")
        )

        return Response({
            "success": True,
            "bot_id": bot.id,
            "bot_username": bot.bot_username
        })