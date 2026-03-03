from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.views import ApiViewSet


class UsersViewSet(ApiViewSet):

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
