from apps.core.mixins import UserScopedMixin
from apps.core.views import ApiViewSet

from .models import Comment


class CommentsViewSet(UserScopedMixin, ApiViewSet):
    resource_label = "댓글"

    @property
    def allowed_includes(self):
        return ["post"]

    def get_base_queryset(self):
        return Comment.objects.order_by("-created_at")
