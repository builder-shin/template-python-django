from django.db.models import Model
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import Post


class PostSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    user = ResourceRelatedField(read_only=True)
    comments = ResourceRelatedField(many=True, read_only=True)

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
            "user",
            "comments",
        ]
        read_only_fields = ["view_count", "published_at", "created_at", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        # For unsaved instances (e.g. `new` action), remove reverse FK relations
        # that require a PK to resolve. The JSON:API renderer calls .all() on the
        # manager directly, which raises ValueError for instances without a PK.
        instance = getattr(self, "instance", None)
        if isinstance(instance, Model) and instance.pk is None:
            fields.pop("comments", None)
        return fields
