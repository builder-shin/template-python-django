from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import Member

STATUS_LABELS_KO = {
    Member.Status.ACTIVE: "활성",
    Member.Status.SUSPENDED: "정지",
    Member.Status.WITHDRAWN: "탈퇴",
}


class MemberSerializer(HookableSerializerMixin, serializers.ModelSerializer):
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

    def get_status_label(self, obj):
        return STATUS_LABELS_KO.get(obj.status, obj.get_status_display())

    def get_display_name(self, obj):
        return obj.display_name()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["links"] = {
            "self": f"/api/v1/members/{instance.pk}",
        }
        return data
