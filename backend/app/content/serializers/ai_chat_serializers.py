from rest_framework import serializers
from content.models.ai_chat import AIChatSession, AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ["id", "role", "content", "created_at"]


class AIChatSessionSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True)

    class Meta:
        model = AIChatSession
        fields = ["id", "title", "messages", "created_at"]
