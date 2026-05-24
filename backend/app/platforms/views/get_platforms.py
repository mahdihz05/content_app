from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from utils.api_response import api_response
from platforms.models import Platform


@csrf_exempt
@login_required
def get_platforms(request):
    if request.method == 'GET':
        platforms = Platform.objects.all()
        platform_list = []
        for p in platforms:
            platform_list.append({
                'id':p.id,
                'name':p.name,
                'is_open':p.is_open,
            })

        return api_response(success=True,
                            message='Platforms List loaded successfully',
                            data=platform_list,
                            status_code=status.HTTP_200_OK)
    return api_response(success=False,
                        error='method not allowed',
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
