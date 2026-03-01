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

    select_for_includes = {
        "__all__": [],
    }
    prefetch_for_includes = {
        "post": ["post"],
    }

    def get_queryset(self):
        return Comment.objects.annotate(_reply_count=Count("replies"))

    def get_index_scope(self):
        return Comment.objects.all()
