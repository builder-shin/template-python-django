import django_filters

from apps.core.filters import TIMESTAMP_LOOKUPS

from .models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "nickname": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "date_joined": TIMESTAMP_LOOKUPS,
        }
