from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from apps.core.mixins.crud_actions import HookableSerializerMixin
from apps.members.models import Member

from .models import Post


class PostSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    member = ResourceRelatedField(queryset=Member.objects.all(), required=False)

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "view_count",
            "status",
            "published_at",
            "created_at",
            "updated_at",
            "member",
            "external_id",
        ]
        read_only_fields = ["member", "view_count", "published_at", "created_at", "updated_at"]
