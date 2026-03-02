from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import JsonApiError
from apps.core.mixins.owned_resource import OwnedResourceMixin
from apps.core.views import ApiViewSet

from .filters import MemberFilter
from .models import Member
from .serializers import MemberSerializer


class MembersViewSet(OwnedResourceMixin, ApiViewSet):
    serializer_class = MemberSerializer
    filterset_class = MemberFilter
    queryset = Member.objects.all()
    resource_label = "프로필"

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        try:
            member = Member.objects.get(user_id=request.user.id)
        except Member.DoesNotExist as err:
            raise JsonApiError("NotFound", "프로필이 존재하지 않습니다.", 404) from err
        serializer = self.get_serializer(member)
        return Response(serializer.data)
