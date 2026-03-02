from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import Post


class PostSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    days_since_published = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    is_publishable = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

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
            "user_id",
            "external_id",
            "days_since_published",
            "summary",
            "author_name",
            "is_publishable",
            "comment_count",
        ]
        read_only_fields = ["user_id", "view_count", "published_at", "created_at", "updated_at"]
        meta_fields = ["days_since_published", "is_publishable"]

    def get_days_since_published(self, obj):
        return obj.days_since_published()

    def get_summary(self, obj):
        return obj.summary()

    def get_author_name(self, obj):
        return obj.author_name()

    def get_is_publishable(self, obj):
        return obj.publishable()

    def get_comment_count(self, obj):
        return getattr(obj, "_comment_count", obj.comment_count())
