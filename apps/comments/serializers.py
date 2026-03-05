from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from apps.core.mixins.crud_actions import HookableSerializerMixin
from apps.posts.models import Post

from .models import Comment


class CommentSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    post = ResourceRelatedField(queryset=Post.objects.all())
    parent = ResourceRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    user = ResourceRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "post",
            "content",
            "parent",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_post(self, value):
        if value.status != Post.Status.PUBLISHED:
            raise serializers.ValidationError("발행된 게시글에만 댓글을 달 수 있습니다.")
        return value
