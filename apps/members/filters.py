import django_filters

from .models import Member


class MemberFilter(django_filters.FilterSet):
    class Meta:
        model = Member
        fields = {
            "nickname": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "user_id": ["exact", "in"],
            "created_at": ["exact", "gt", "gte", "lt", "lte"],
            "updated_at": ["exact", "gt", "gte", "lt", "lte"],
        }
