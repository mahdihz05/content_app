from rest_framework import status

from platforms.models import Platform, SocialAccount
from utils.api_response import api_response

def connect_account(request):
    """
    this is pass , with social account data in database connect to selected platform with api or just check to available platform
    :param request:
    :return:
    """
    print('connect account is proccessing ...')

    return api_response(success=True,
                        message="account connected successfully",
                        status_code=status.HTTP_200_OK)



def disconnect_account(request):
    """
    for edit database data
    :param request:
    :return:
    """
    print('disconnect account is proccessing ...')

    return api_response(success=True,
                        message="account disconnected successfully",
                        status_code=status.HTTP_200_OK)