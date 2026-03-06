from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet


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
        return ["user", "comments"]

    def get_index_scope(self):
        """인증된 사용자는 자신의 글만 조회 (내 글 목록).
        비인증 사용자에게는 전체 공개 글이 노출됨 (list permission이 AllowAny이므로).
        전체 글 목록이 필요하면 별도 action을 추가할 것."""
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
