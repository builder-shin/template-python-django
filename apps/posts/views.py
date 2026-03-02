from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import JsonApiError
from apps.core.mixins.owned_resource import OwnedResourceMixin
from apps.core.views import ApiViewSet

from .filters import PostFilter
from .models import Post
from .serializers import PostSerializer


class PostsViewSet(OwnedResourceMixin, ApiViewSet):
    serializer_class = PostSerializer
    filterset_class = PostFilter
    resource_label = "글"

    @property
    def allowed_includes(self):
        return ["comments"]

    prefetch_for_includes = {
        "comments": ["comments"],
    }

    def get_base_queryset(self):
        return Post.objects.annotate(_comment_count=Count("comments"))

    def get_index_scope(self):
        return self.get_base_queryset().filter(user_id=self.request.user.id)

    def upsert_after_init(self, instance):
        if not instance.user_id:
            instance.user_id = self.request.user.id

    def upsert_find_params(self):
        body = self._parse_raw_body()
        external_id = body.get("data", {}).get("attributes", {}).get("external_id")
        if not external_id:
            return None
        return {"external_id": external_id}

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, *args, **kwargs):
        instance = self.get_object()
        self._check_ownership(instance, "발행")
        if not instance.publish():
            raise JsonApiError("UnprocessableEntity", "발행할 수 없는 상태입니다.", 422)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
