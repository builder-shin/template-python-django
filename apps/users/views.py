from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import JsonApiError
from apps.core.mixins import UserScopedMixin
from apps.core.views import ApiViewSet


class UsersViewSet(UserScopedMixin, ApiViewSet):
    resource_label = "프로필"

    def _check_ownership(self, instance, action_label: str) -> None:
        if instance.id != self.request.user.id:
            raise JsonApiError(
                "Forbidden",
                f"본인의 {self.resource_label}만 {action_label}할 수 있습니다.",
                403,
            )

    def create_after_init(self, instance) -> None:
        pass

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
