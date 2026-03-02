from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import Member


class MemberSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "user_id",
            "nickname",
            "bio",
            "avatar_url",
            "status",
            "created_at",
            "updated_at",
            "display_name",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at"]

    def get_display_name(self, obj):
        return obj.display_name()
