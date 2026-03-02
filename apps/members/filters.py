import django_filters

from apps.core.filters import TIMESTAMP_LOOKUPS

from .models import Member


class MemberFilter(django_filters.FilterSet):
    class Meta:
        model = Member
        fields = {
            "nickname": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "user_id": ["exact", "in"],
            "created_at": TIMESTAMP_LOOKUPS,
            "updated_at": TIMESTAMP_LOOKUPS,
        }
