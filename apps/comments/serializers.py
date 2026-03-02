from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from apps.core.mixins.crud_actions import HookableSerializerMixin
from apps.posts.models import Post

from .models import Comment


class CommentSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    post = ResourceRelatedField(queryset=Post.objects.all())
    parent = ResourceRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    author_name = serializers.SerializerMethodField()
    is_reply = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "post",
            "content",
            "user_id",
            "parent",
            "created_at",
            "updated_at",
            "author_name",
            "is_reply",
            "reply_count",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at"]

    def get_author_name(self, obj):
        return obj.author_name()

    def get_is_reply(self, obj):
        return obj.is_reply()

    def get_reply_count(self, obj):
        return getattr(obj, "_reply_count", obj.reply_count())
