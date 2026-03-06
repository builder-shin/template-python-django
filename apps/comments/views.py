from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet

from .models import Comment


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

    def get_base_queryset(self):
        return Comment.objects.select_related("post", "user").order_by("-created_at")
