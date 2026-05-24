from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from messaging_automation.models.account import MessagingAccount

from messaging_automation.serializers.account_serializer import (
    MessagingAccountSerializer
)


class AccountListAPIView(APIView):

    def get(self, request):

        accounts = MessagingAccount.objects.all().order_by("-id")

        serializer = MessagingAccountSerializer(
            accounts,
            many=True
        )

        return Response(serializer.data)


class AccountCreateAPIView(APIView):

    def post(self, request):

        serializer = MessagingAccountSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )