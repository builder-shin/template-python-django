from django.db.models import Count

from apps.core.mixins.owned_resource import OwnedResourceMixin
from apps.core.views import ApiViewSet

from .filters import CommentFilter
from .models import Comment
from .serializers import CommentSerializer


class CommentsViewSet(OwnedResourceMixin, ApiViewSet):
    serializer_class = CommentSerializer
    filterset_class = CommentFilter
    resource_label = "댓글"

    @property
    def allowed_includes(self):
        return ["post"]

    prefetch_for_includes = {
        "post": ["post"],
    }

    def get_base_queryset(self):
        return Comment.objects.annotate(_reply_count=Count("replies"))
