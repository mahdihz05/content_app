from django.shortcuts import render
from utils.api_response import api_response
from user.serializers import RegisterSerializer, UserSerializer
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from user.models import CustomUser # فرض می‌کنیم مدل CustomUser در این مسیر قرار دارد
from rest_framework import status

# --- get_users ---
@login_required
def get_users(request):
    if request.method == 'GET':
        try:
            users = CustomUser.objects.all()
            serializer = UserSerializer(users, many=True)
            return api_response(success=True, message='users successfully fetched', data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error in get_users: {e}")
            return api_response(success=False, error='خطا در دریافت لیست کاربران', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return api_response(success=False, error='روش مجاز نیست', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


# --- get_user ---
@csrf_exempt
@login_required
def get_user(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            phone_number = request.GET.get('phone_number')

            if not phone_number and not user_id:
                return api_response(success=False, error='شماره تلفن یا شناسه کاربر الزامی است', status_code=status.HTTP_400_BAD_REQUEST)

            user = None
            try:
                if user_id:
                    user = CustomUser.objects.get(id=user_id)
                elif phone_number:
                    user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                return api_response(success=False, error='کاربر یافت نشد', status_code=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user)
            return api_response(success=True, message='کاربر با موفقیت یافت شد', data=serializer.data, status_code=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in get_user: {e}")
            return api_response(success=False, error='خطا در دریافت اطلاعات کاربر', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return api_response(success=False, error='روش مجاز نیست', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)




def home(request):
    return render(request, 'user/landing.html')
