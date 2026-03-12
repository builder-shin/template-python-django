from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.filters import TIMESTAMP_LOOKUPS
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet


class CommentsViewSet(ApiViewSet):
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
        return ["post"]

    @property
    def allowed_filters(self):
        return {
            "content": ["exact", "icontains"],
            "user": ["exact", "in"],
            "post": ["exact", "in"],
            "parent": ["exact", "isnull"],
            "created_at": TIMESTAMP_LOOKUPS,
            "updated_at": TIMESTAMP_LOOKUPS,
        }
