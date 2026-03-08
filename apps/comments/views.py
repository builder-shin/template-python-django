from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet


class CommentsViewSet(ApiViewSet):
    select_related_extra = ["user"]

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
