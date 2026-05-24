import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.shortcuts import get_object_or_404

from content.models import ContentItem
from content.models import Keyword
from utils.api_response import api_response

@csrf_exempt
@login_required
def create_keyword(request):
    if request.method != 'POST':
        return api_response(
            success=False,
            error='method not allowed',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api_response(
            success=False,
            error='invalid json',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    content_item_id = payload.get('content_item_id')
    keyword_text = payload.get('keyword')
    source = payload.get('source')

    if not content_item_id or not keyword_text or not source:
        return api_response(
            success=False,
            error='content_item_id, keyword and source are required',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        content_item = ContentItem.objects.get(
            id=content_item_id,
            campaign__user=user
        )
    except ContentItem.DoesNotExist:
        return api_response(
            success=False,
            error='content item not found',
            status_code=status.HTTP_404_NOT_FOUND
        )

    # اصلاح نام فیلد به is_processed
    keyword = Keyword.objects.create(
        content_item=content_item,
        keyword=keyword_text,
        source=source
    )

    return api_response(
        success=True,
        message='keyword created',
        data={
            "id": keyword.id,
            "content_item_id": content_item.id,
            "keyword": keyword.keyword,
            "source": keyword.source,
            # "is_processed": keyword.is_processed
        },
        status_code=status.HTTP_201_CREATED
    )



@csrf_exempt
@login_required
def update_keyword(request):
    if request.method != 'POST':
        return api_response(
            success=False,
            error='method not allowed',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api_response(
            success=False,
            error='invalid json',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    keyword_id = payload.get('keyword_id')

    if not keyword_id:
        return api_response(
            success=False,
            error='keyword_id is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        keyword = Keyword.objects.get(
            id=keyword_id,
            content_item__campaign__user=user
        )
    except Keyword.DoesNotExist:
        return api_response(
            success=False,
            error='keyword not found',
            status_code=status.HTTP_404_NOT_FOUND
        )

    if 'keyword' in payload:
        keyword.keyword = payload['keyword']

    if 'source' in payload:
        keyword.source = payload['source']

    # چون اسم واقعی فیلد در مدل همین است
    if 'is_proccessed' in payload:
        keyword.is_proccessed = payload['is_proccessed']

    keyword.save()

    return api_response(
        success=True,
        message='keyword updated',
        data={
            "id": keyword.id,
            "keyword": keyword.keyword,
            "source": keyword.source,
            "is_proccessed": keyword.is_proccessed
        },
        status_code=status.HTTP_200_OK
    )


@csrf_exempt
@login_required
def delete_keyword(request):
    if request.method != 'DELETE':
        return api_response(
            success=False,
            error='method not allowed',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api_response(
            success=False,
            error='invalid json',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    keyword_id = payload.get('keyword_id')

    if not keyword_id:
        return api_response(
            success=False,
            error='keyword_id is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        keyword = Keyword.objects.get(
            id=keyword_id,
            content_item__campaign__user=user
        )
        keyword.delete()

        return api_response(
            success=True,
            message='keyword deleted',
        )
    except Exception as e:
        return api_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
@login_required
def bulk_create_keywords(request):
    if request.method != "POST":
        return api_response(
            success=False,
            error="method not allowed",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api_response(
            success=False,
            error="invalid json body",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    content_item_id = payload.get("content_item_id")
    keywords_list = payload.get("keywords")

    print('---------------- bulk_create_keywords payload ----------------')
    print(payload)
    print('---------------- keywords_list ----------------')
    print(keywords_list)

    if not content_item_id:
        return api_response(
            success=False,
            error="content_item_id is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if keywords_list is None or not isinstance(keywords_list, list):
        return api_response(
            success=False,
            error="keywords list is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        content_item = ContentItem.objects.get(
            id=content_item_id,
            campaign__user=user
        )
    except ContentItem.DoesNotExist:
        return api_response(
            success=False,
            error="content item not found or not allowed",
            status_code=status.HTTP_404_NOT_FOUND
        )

    keyword_objects = []

    for k in keywords_list:
        if not isinstance(k, dict):
            continue

        text = k.get("keyword")
        source = k.get("source")

        # # چون فیلد واقعی مدل همین است:
        # is_proccessed_val = k.get("is_proccessed", False)
        #
        # # اگر فرانت هنوز is_processed فرستاد، این هم ساپورت شود
        # if "is_processed" in k and "is_proccessed" not in k:
        #     is_proccessed_val = k.get("is_processed", False)

        if not text or not source:
            continue

        keyword_objects.append(
            Keyword(
                content_item=content_item,
                keyword=text,
                source=source,
                # is_proccessed=is_proccessed_val
            )
        )

    if not keyword_objects:
        return api_response(
            success=False,
            error="No valid keywords provided",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    created_items = Keyword.objects.bulk_create(keyword_objects)

    output = []
    for obj in created_items:
        output.append({
            "id": obj.id,
            "keyword": obj.keyword,
            "source": obj.source,
            # "is_proccessed": obj.is_proccessed
        })

    return api_response(
        success=True,
        message=f"{len(output)} keywords saved successfully",
        data=output,
        status_code=status.HTTP_201_CREATED
    )

