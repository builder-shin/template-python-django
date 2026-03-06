from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet

from .models import Post


class PostsViewSet(ApiViewSet):
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def create_after_init(self, instance) -> None:
        instance.user = self.request.user

    @property
    def allowed_includes(self):
        return ["comments"]

    def get_base_queryset(self):
        return Post.objects.select_related("user").order_by("-created_at")

    def get_index_scope(self):
        qs = super().get_index_scope()
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs

    def upsert_after_init(self, instance):
        if not instance.user_id:
            instance.user = self.request.user

    def upsert_find_params(self):
        body = self._parse_raw_body()
        external_id = body.get("data", {}).get("attributes", {}).get("external_id")
        if not external_id:
            return None
        return {"external_id": external_id}
