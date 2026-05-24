from django.contrib.auth.decorators import login_required
from rest_framework import status
from utils.api_response import api_response
import json
from ai.pipelines.create_content import core


@login_required
def create_content_chat(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        message = payload.get('message')
        if not message:
            return api_response(
                success=False,
                error='Message is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )


    return api_response(
        success=False,
        error='method not allowed',
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )