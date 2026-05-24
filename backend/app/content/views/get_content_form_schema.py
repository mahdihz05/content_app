from django.contrib.auth.decorators import login_required
from rest_framework import status
from utils.api_response import api_response
from content.models import ContentFormSchema

@login_required
def get_content_form_schema(request):
    if request.method == 'GET':
        platform_id = request.GET.get('platform_id')
        if platform_id is None:
            return api_response(success=False,
                                error="Platform ID is required",
                                status_code=status.HTTP_400_BAD_REQUEST)


        schema = ContentFormSchema.objects.filter(platform__id=platform_id).first()
        if schema is None:
            return api_response(success=False,
                                error="Platform ID is invalid",
                                status_code=status.HTTP_400_BAD_REQUEST)
        result = [{
            'id':schema.id,
            'schema':schema.schema,
            'description':schema.description,
            'is_active':schema.is_active,
        }]
        return api_response(success=True,
                            data=result,
                            message="schema successfully loaded ...",
                            status_code=status.HTTP_200_OK)
    return api_response(success=False,
                        error="method not allowed",
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED)