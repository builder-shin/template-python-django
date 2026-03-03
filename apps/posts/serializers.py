from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import Post


class PostSerializer(HookableSerializerMixin, serializers.ModelSerializer):
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
            "external_id",
        ]
        read_only_fields = ["view_count", "published_at", "created_at", "updated_at"]
