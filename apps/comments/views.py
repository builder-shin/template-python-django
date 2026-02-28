from rest_framework_json_api.filters import QueryParameterValidationFilter, OrderingFilter
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.core.views import ApiViewSet
from apps.core.mixins.crud_actions import CrudActionsMixin
from apps.core.permissions import IsAuthenticated
from apps.core.filters import AllowedIncludesFilter
from apps.core.exceptions import JsonApiError

from .models import Comment
from .serializers import CommentSerializer
from .filters import CommentFilter


class CommentsViewSet(CrudActionsMixin, ApiViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CommentFilter
    filter_backends = [
        QueryParameterValidationFilter,
        OrderingFilter,
        DjangoFilterBackend,
        SearchFilter,
        AllowedIncludesFilter,
    ]

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
        return Comment.objects.all()

    def get_index_scope(self):
        return Comment.objects.all()

    def create_after_init(self, instance):
        instance.user_id = self.request.user.id

    def update_after_init(self, instance):
        if instance.user_id != self.request.user.id:
            raise JsonApiError("Forbidden", "본인의 댓글만 수정할 수 있습니다.", 403)

    def destroy_after_init(self, instance):
        if instance.user_id != self.request.user.id:
            raise JsonApiError("Forbidden", "본인의 댓글만 삭제할 수 있습니다.", 403)
