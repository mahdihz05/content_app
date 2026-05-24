from utils.api_response import api_response
from user.serializers import RegisterSerializer, UserSerializer
import json
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from rest_framework import status


# --- register_view ---
@csrf_exempt
def register_view(request):

    if request.user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return api_response(
                success=False,
                error='داده‌های ارسالی نامعتبرند',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return api_response(
                success=False,
                error='خطایی رخ داد',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = RegisterSerializer(data=payload)

        if serializer.is_valid():
            user = serializer.save()
            login(request, user)

            next_url = request.GET.get("next") or "/dashboard"

            return api_response(
                success=True,
                message='ثبت‌نام با موفقیت انجام شد',
                redirect=next_url,
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )

        return api_response(
            success=False,
            error=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


def register_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    return render(request, 'user/register.html')
