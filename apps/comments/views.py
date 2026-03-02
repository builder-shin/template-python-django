from django.db.models import Count

from apps.core.exceptions import JsonApiError
from apps.core.views import ApiViewSet

from .filters import CommentFilter
from .models import Comment
from .serializers import CommentSerializer


class CommentsViewSet(ApiViewSet):
    serializer_class = CommentSerializer
    filterset_class = CommentFilter

    def _check_ownership(self, instance, action_label: str) -> None:
        if str(instance.user_id) != str(self.request.user.id):
            raise JsonApiError("Forbidden", f"본인의 댓글만 {action_label}할 수 있습니다.", 403)

    def create_after_init(self, instance) -> None:
        instance.user_id = str(self.request.user.id)

    def update_after_init(self, instance) -> None:
        self._check_ownership(instance, "수정")

    def destroy_after_init(self, instance) -> None:
        self._check_ownership(instance, "삭제")

    @property
    def allowed_includes(self):
        return ["post"]

    prefetch_for_includes = {
        "post": ["post"],
    }

    def get_base_queryset(self):
        return Comment.objects.annotate(_reply_count=Count("replies"))
