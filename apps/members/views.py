from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.views import ApiViewSet
from apps.core.mixins.owned_resource import OwnedResourceMixin
from apps.core.exceptions import JsonApiError

from .models import Member
from .serializers import MemberSerializer
from .filters import MemberFilter


class MembersViewSet(OwnedResourceMixin, ApiViewSet):
    serializer_class = MemberSerializer
    filterset_class = MemberFilter
    resource_label = "프로필"

    def get_queryset(self):
        return Member.objects.all()

    def get_index_scope(self):
        return Member.objects.all()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        try:
            member = Member.objects.get(user_id=request.user.id)
        except Member.DoesNotExist:
            raise JsonApiError("NotFound", "프로필이 존재하지 않습니다.", 404)
        serializer = self.get_serializer(member)
        return Response(serializer.data)
