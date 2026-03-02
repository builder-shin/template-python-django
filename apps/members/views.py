from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import JsonApiError
from apps.core.views import ApiViewSet

from .filters import MemberFilter
from .models import Member
from .serializers import MemberSerializer


class MembersViewSet(ApiViewSet):
    serializer_class = MemberSerializer
    filterset_class = MemberFilter
    queryset = Member.objects.all()

    def _check_ownership(self, instance, action_label: str) -> None:
        if str(instance.user_id) != str(self.request.user.id):
            raise JsonApiError("Forbidden", f"본인의 프로필만 {action_label}할 수 있습니다.", 403)

    def create_after_init(self, instance) -> None:
        instance.user_id = str(self.request.user.id)

    def update_after_init(self, instance) -> None:
        self._check_ownership(instance, "수정")

    def destroy_after_init(self, instance) -> None:
        self._check_ownership(instance, "삭제")

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        try:
            member = Member.objects.get(user_id=request.user.id)
        except Member.DoesNotExist as err:
            raise JsonApiError("NotFound", "프로필이 존재하지 않습니다.", 404) from err
        serializer = self.get_serializer(member)
        return Response(serializer.data)
