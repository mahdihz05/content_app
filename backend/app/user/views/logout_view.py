from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from utils.api_response import api_response
from rest_framework import status

@csrf_exempt
def logout_view(request):

    if not request.user.is_authenticated:
        return api_response(
            success=False,
            error="کاربر وارد نشده است",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    logout(request)

    return api_response(
        success=True,
        redirect="auth/login",
        status_code=status.HTTP_200_OK
    )
