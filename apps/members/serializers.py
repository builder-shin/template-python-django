from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin
from apps.core.serializers import AutoLinksMixin, StatusLabelMixin

from .models import Member


class MemberSerializer(AutoLinksMixin, StatusLabelMixin, HookableSerializerMixin, serializers.ModelSerializer):
    resource_path = "members"
    status_labels_ko = {
        Member.Status.ACTIVE: "활성",
        Member.Status.SUSPENDED: "정지",
        Member.Status.WITHDRAWN: "탈퇴",
    }

    status_label = serializers.SerializerMethodField()
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
            "status_label",
            "display_name",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at"]

    def get_display_name(self, obj):
        return obj.display_name()
