from apps.core.views import ApiViewSet

from .models import Comment


class CommentsViewSet(ApiViewSet):

    def create_after_init(self, instance) -> None:
        instance.user = self.request.user

    @property
    def allowed_includes(self):
        return ["post"]

    def get_base_queryset(self):
        return Comment.objects.order_by("-created_at")
