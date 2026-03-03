from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import Member


class MemberSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "nickname",
            "bio",
            "avatar_url",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
