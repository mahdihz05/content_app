from django.urls import path
from .views import (campaign_detail,
                    campaign_list,
                    create_campaign,
                    update_campaign,
                    delete_campaign,
                    get_goal_list,
                    get_goal_schema,
                    get_all_goal_schema
                    )
urlpatterns = [
    path('api/v1/campaign_detail', campaign_detail, name='campaign_detail-api-v1'),
    path('api/v1/campaign_list', campaign_list, name='campaign_list-api-v1'),
    path('api/v1/create_campaign', create_campaign, name='create_campaign-api-v1'),
    path('api/v1/update_campaign', update_campaign, name='update_campaign-api-v1'),
    path('api/v1/delete_campaign', delete_campaign, name='delete_campaign-api-v1'),



    path('api/v1/get_goal_list', get_goal_list, name='get_goal_list-api-v1'),

    path('api/v1/get_goal_schema', get_goal_schema, name='get_goal_schema-api-v1'),
    path('api/v1/get_all_goal_schema', get_all_goal_schema, name='get_all_goal_schema-api-v1'),



]