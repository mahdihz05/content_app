import re
import uuid


CORRELATION_ID_HEADER = 'X-Correlation-ID'
_SAFE_CORRELATION_ID = re.compile(r'^[A-Za-z0-9._-]{1,128}$')


class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        supplied_id = request.headers.get(CORRELATION_ID_HEADER, '')
        correlation_id = (
            supplied_id
            if _SAFE_CORRELATION_ID.fullmatch(supplied_id)
            else str(uuid.uuid4())
        )
        request.correlation_id = correlation_id
        response = self.get_response(request)
        response[CORRELATION_ID_HEADER] = correlation_id
        return response
