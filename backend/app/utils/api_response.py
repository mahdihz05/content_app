from django.http import JsonResponse
import json


def api_response(success, message=None, data=None, error=None, redirect=None, status_code=200):
    response = {
        'success': success,
    }
    if message:
        response['message'] = message
    if data:
        response['data'] = data
    if error:
        response['error'] = str(error)  # تبدیل خطای غیرقابل سریال‌سازی به رشته
    if redirect:
        response['redirect'] = redirect
    return JsonResponse(response, status=status_code)
