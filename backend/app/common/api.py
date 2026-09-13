from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView


def error_payload(request, code, message, details=None):
    return {
        'error': {
            'version': 'v2',
            'code': code,
            'message': message,
            'details': details or {},
            'correlation_id': getattr(request, 'correlation_id', ''),
        }
    }


class V2APIView(APIView):
    """V2-only error normalization that leaves legacy API responses unchanged."""

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            response_status = status.HTTP_401_UNAUTHORIZED
            code = 'authentication_required'
            message = 'Authentication is required.'
        elif isinstance(exc, PermissionDenied):
            response_status = status.HTTP_403_FORBIDDEN
            code = 'permission_denied'
            message = 'Permission denied.'
        elif isinstance(exc, APIException):
            response_status = exc.status_code
            code = exc.default_code
            message = str(exc.detail)
        else:
            return super().handle_exception(exc)

        return Response(
            error_payload(self.request, code, message),
            status=response_status,
        )
