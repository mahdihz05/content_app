from django.db import DatabaseError, connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.api import V2APIView, error_payload


def database_is_ready():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        return False
    return True


class HealthView(V2APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'status': 'ok', 'version': 'v2'})


class ReadinessView(V2APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not database_is_ready():
            return Response(
                error_payload(
                    request,
                    'service_not_ready',
                    'A required service is unavailable.',
                ),
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'status': 'ready', 'version': 'v2'})
