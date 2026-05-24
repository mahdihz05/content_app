from utils.api_response import api_response
import json
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from user.models import CustomUser # فرض می‌کنیم مدل CustomUser در این مسیر قرار دارد
from rest_framework import status


@csrf_exempt
def login_view(request):

    if request.user.is_authenticated:
        return redirect('/dashboard')

    if request.method == "POST":
        try:
            payload = json.loads(request.body)

            phone_number = payload.get("phone_number")
            password = payload.get("password")

            if not phone_number or not password:
                return api_response(
                    success=False,
                    error="شماره تلفن یا رمز عبور الزامی است",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                user = None

            if user and user.check_password(password):

                login(request, user)

                next_url = request.GET.get("next") or "/dashboard"

                return api_response(
                    success=True,
                    redirect=next_url,
                    status_code=status.HTTP_200_OK
                )

            return api_response(
                success=False,
                error="شماره تلفن یا رمز عبور نادرست است",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(f"Login error: {e}")

            return api_response(
                success=False,
                error="خطا در پردازش درخواست ورود",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    return render(request, "user/login.html")

