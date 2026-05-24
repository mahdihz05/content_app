from django.contrib.auth.decorators import login_required
from rest_framework import status
from utils.api_response import api_response
from platforms.models import SocialAccount

@login_required
def list_accounts(request):
    if request.method == 'GET':
        user = request.user
        try:
            accounts = []
            social_accounts = SocialAccount.objects.filter(user_id=user.id).all().order_by('-id')
            for sa in social_accounts:
                if sa.is_active:
                    accounts.append({
                        'id': sa.id,
                        'platform': sa.platform,
                        'metadata': sa.metadata,
                    })
            return api_response(success=True,
                                message=f'account lists for user with {user.id} id founded',
                                data=accounts,
                                status_code=status.HTTP_200_OK)
        except Exception as e:
            return api_response(success=False,
                                error=str(e),
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

