from rest_framework import serializers

from .models import Workspace, WorkspaceMembership


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ('public_id', 'name', 'slug')


class MembershipSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer(read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceMembership
        fields = ('id', 'workspace', 'user', 'role', 'is_active', 'is_default', 'created_at')

    def get_user(self, membership):
        return {
            'id': membership.user_id,
            'name': membership.user.name,
            'phone_number': membership.user.phone_number,
        }


class SwitchWorkspaceSerializer(serializers.Serializer):
    workspace_id = serializers.UUIDField()
    make_default = serializers.BooleanField(default=False)


class MembershipCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    role = serializers.ChoiceField(choices=WorkspaceMembership.Role.choices)
    is_default = serializers.BooleanField(default=False)


class MembershipUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=WorkspaceMembership.Role.choices, required=False)
    is_active = serializers.BooleanField(required=False)
    is_default = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('At least one field is required.')
        return attrs
