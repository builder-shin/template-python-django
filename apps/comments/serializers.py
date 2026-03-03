from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from apps.core.mixins.crud_actions import HookableSerializerMixin
from apps.members.models import Member
from apps.posts.models import Post

from .models import Comment


class CommentSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    post = ResourceRelatedField(queryset=Post.objects.all())
    parent = ResourceRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    member = ResourceRelatedField(queryset=Member.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = [
            "post",
            "content",
            "member",
            "parent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["member", "created_at", "updated_at"]
