from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet

from .models import Comment


class CommentsViewSet(ApiViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create_after_init(self, instance) -> None:
        instance.user = self.request.user

    @property
    def allowed_includes(self):
        return ["post"]

    def get_base_queryset(self):
        return Comment.objects.select_related("post", "user").order_by("-created_at")
