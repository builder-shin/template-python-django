from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_json_api.filters import QueryParameterValidationFilter, OrderingFilter
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.core.views import ApiViewSet
from apps.core.mixins.crud_actions import CrudActionsMixin
from apps.core.permissions import IsAuthenticated
from apps.core.filters import AllowedIncludesFilter
from apps.core.exceptions import JsonApiError

from .models import Member
from .serializers import MemberSerializer
from .filters import MemberFilter


class MembersViewSet(CrudActionsMixin, ApiViewSet):
    serializer_class = MemberSerializer
    # permission_classes = [IsAuthenticated]
    filterset_class = MemberFilter
    filter_backends = [
        QueryParameterValidationFilter,
        OrderingFilter,
        DjangoFilterBackend,
        SearchFilter,
        AllowedIncludesFilter,
    ]

    def get_queryset(self):
        return Member.objects.all()

    def get_index_scope(self):
        return Member.objects.all()

    def create_after_init(self, instance):
        instance.user_id = self.request.user.id

    def update_after_init(self, instance):
        if instance.user_id != self.request.user.id:
            raise JsonApiError("Forbidden", "본인의 프로필만 수정할 수 있습니다.", 403)

    def destroy_after_init(self, instance):
        if instance.user_id != self.request.user.id:
            raise JsonApiError("Forbidden", "본인의 프로필만 삭제할 수 있습니다.", 403)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        try:
            member = Member.objects.get(user_id=request.user.id)
        except Member.DoesNotExist:
            raise JsonApiError("NotFound", "프로필이 존재하지 않습니다.", 404)
        serializer = self.get_serializer(member)
        return Response(serializer.data)
