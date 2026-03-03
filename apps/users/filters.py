import django_filters

from .models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "nickname": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "date_joined": ["exact", "gt", "gte", "lt", "lte"],
        }
