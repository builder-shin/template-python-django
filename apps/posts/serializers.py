from django.utils import timezone
from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin
from apps.core.serializers import AutoLinksMixin, StatusLabelMixin

from .models import Post


class PostSerializer(AutoLinksMixin, StatusLabelMixin, HookableSerializerMixin, serializers.ModelSerializer):
    resource_path = "posts"
    status_labels_ko = {
        Post.Status.DRAFT: "초안",
        Post.Status.PUBLISHED: "게시됨",
        Post.Status.ARCHIVED: "보관됨",
    }

    days_since_published = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
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
            "status_label",
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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # AutoLinksMixin이 data["links"]["self"]를 이미 설정함
        data["links"]["comments"] = f"/api/v1/comments?filter[post_id_eq]={instance.pk}"

        if instance.status == instance.Status.PUBLISHED:
            data["links"]["public_url"] = f"/posts/{instance.pk}"

        request = self.context.get("request")
        if (
            request
            and hasattr(request, "user")
            and request.user
            and str(getattr(request.user, "id", None)) == str(instance.user_id)
        ):
            data["edit_url"] = f"/api/v1/posts/{instance.pk}"

        data.setdefault("meta", {}).update(
            {
                "copyright": f"{timezone.now().year} Template Inc.",
            }
        )

        return data
