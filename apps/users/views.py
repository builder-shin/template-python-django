from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.core.views import ApiViewSet


class IsOwnerUser(BasePermission):
    """Users can only update their own profile."""

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.id == request.user.id


class UsersViewSet(ApiViewSet):
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "me":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerUser()]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
