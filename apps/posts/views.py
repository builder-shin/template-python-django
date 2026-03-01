from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_json_api.filters import QueryParameterValidationFilter, OrderingFilter
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import Count

from apps.core.views import ApiViewSet
from apps.core.mixins.crud_actions import CrudActionsMixin
from apps.core.permissions import IsAuthenticated
from apps.core.filters import AllowedIncludesFilter
from apps.core.exceptions import JsonApiError

from .models import Post
from .serializers import PostSerializer
from .filters import PostFilter


class PostsViewSet(CrudActionsMixin, ApiViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PostFilter
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    filter_backends = [
        QueryParameterValidationFilter,
        OrderingFilter,
        DjangoFilterBackend,
        SearchFilter,
        AllowedIncludesFilter,
    ]

    @property
    def allowed_includes(self):
        return ["comments"]

    select_for_includes = {
        "__all__": [],
    }
    prefetch_for_includes = {
        "comments": ["comments"],
    }

    def get_queryset(self):
        return Post.objects.annotate(_comment_count=Count("comments"))

    def get_index_scope(self):
        user = self.request.user
        if user and hasattr(user, "id") and user.id:
            return Post.objects.by_user(user.id)
        return Post.objects.none()

    def create_after_init(self, instance):
        instance.user_id = self.request.user.id

    def create_after_save(self, instance, success):
        pass

    def update_after_init(self, instance):
        if instance.user_id != self.request.user.id:
            raise JsonApiError("Forbidden", "본인의 글만 수정할 수 있습니다.", 403)

    def update_after_assign(self, instance):
        pass

    def update_after_save(self, instance, success):
        pass

    def destroy_after_init(self, instance):
        if instance.user_id != self.request.user.id:
            raise JsonApiError("Forbidden", "본인의 글만 삭제할 수 있습니다.", 403)

    def upsert_after_init(self, instance):
        if not instance.user_id:
            instance.user_id = self.request.user.id

    def upsert_find_params(self):
        import json as _json
        try:
            raw = self.request._request.body
            body = _json.loads(raw)
            external_id = body.get("data", {}).get("attributes", {}).get("external_id")
        except Exception:
            external_id = None
        if not external_id:
            return None
        return {"external_id": external_id}

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            raise JsonApiError("Forbidden", "본인의 글만 발행할 수 있습니다.", 403)
        if not instance.publish():
            raise JsonApiError("UnprocessableEntity", "발행할 수 없는 상태입니다.", 422)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
