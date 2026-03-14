from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.filters import TIMESTAMP_LOOKUPS
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.views import ApiViewSet


class UsersViewSet(ApiViewSet):
    ordering = ["-date_joined"]
    owner_field = "id"  # User owns themselves (obj.id == request.user.id)

    @property
    def allowed_filters(self):
        return {
            "nickname": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "date_joined": TIMESTAMP_LOOKUPS,
        }

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        if self.action in ("list", "me"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
