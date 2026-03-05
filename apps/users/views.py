from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.core.views import ApiViewSet


class IsOwnerUser(BasePermission):
    """Users can only update their own profile."""

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.id == request.user.id


class UsersViewSet(ApiViewSet):
    permission_classes = [IsAuthenticated, IsOwnerUser]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
