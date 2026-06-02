from rest_framework import serializers
from messaging_automation.models.account import MessagingAccount

import json


class BulkSendSerializer(serializers.Serializer):

    account_id = serializers.IntegerField()

    message = serializers.CharField(
        required=False,
        allow_blank=True
    )

    message_type = serializers.ChoiceField(
        choices=[
            ("text", "Text"),
            ("image", "Image"),
            ("file", "File"),
        ]
    )

    recipients_json = serializers.CharField()

    delay = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        max_value=60
    )

    scheduled_at = serializers.DateTimeField(
        required=False,
        allow_null=True
    )

    attachment = serializers.FileField(
        required=False,
        allow_null=True
    )

    def validate_account_id(self, value):

        request = self.context.get("request")

        try:

            account = MessagingAccount.objects.get(
                id=value,
                user=request.user,
                is_active=True
            )

        except MessagingAccount.DoesNotExist:

            raise serializers.ValidationError(
                "اکانت معتبر نیست"
            )

        return value

    def validate_recipients_json(self, value):

        try:

            recipients = json.loads(value)

        except Exception:

            raise serializers.ValidationError(
                "فرمت مخاطبین نامعتبر است"
            )

        if not isinstance(recipients, list):

            raise serializers.ValidationError(
                "مخاطبین باید لیست باشند"
            )

        cleaned = []

        for item in recipients:

            item = str(item).strip()

            if item:

                cleaned.append(item)

        cleaned = list(set(cleaned))

        if not cleaned:

            raise serializers.ValidationError(
                "حداقل یک مخاطب وارد کنید"
            )

        return cleaned

    def validate(self, attrs):

        message_type = attrs.get("message_type")

        message = attrs.get("message", "").strip()

        attachment = attrs.get("attachment")

        if message_type == "text" and not message:

            raise serializers.ValidationError({
                "message": "متن پیام الزامی است"
            })

        if message_type in ["image", "file"] and not attachment:

            raise serializers.ValidationError({
                "attachment": "فایل الزامی است"
            })

        return attrs