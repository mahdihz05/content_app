from django.shortcuts import render


def dashboard_page(request):

    return render(
        request,
        "dashboard/messaging_automation/dashboard.html"
    )


def account_list_page(request):

    return render(
        request,
        "dashboard/messaging_automation/account_list.html"
    )


def account_create_page(request):

    return render(
        request,
        "dashboard/messaging_automation/account_create.html"
    )


def campaign_list_page(request):

    return render(
        request,
        "dashboard/messaging_automation/campaign_list.html"
    )


def campaign_create_page(request):

    return render(
        request,
        "dashboard/messaging_automation/campaign_create.html"
    )


def campaign_detail_page(request, campaign_id):

    return render(
        request,
        "dashboard/messaging_automation/campaign_detail.html",
        {
            "campaign_id": campaign_id
        }
    )


def ai_chat_page(request):

    return render(
        request,
        "dashboard/messaging_automation/ai_chat.html"
    )



