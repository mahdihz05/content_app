from django.urls import path
from .views import register_view, login_view, get_user, get_users, register_page, login_page, logout_view

urlpatterns = [
    path('register', register_page, name='register'),
    path('login', login_page, name='login'),
    path('logout', logout_view, name='logout'),



    path('api/v1/register', register_view, name='register-api-v1'),
    path('api/v1/login', login_view, name='login-api-v1'),
    path('api/v1/users', get_users, name='users-api-v1'),
    path('api/v1/user', get_user, name='user-api-v1'),
]