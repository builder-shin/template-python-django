import django_filters

from apps.core.filters import TIMESTAMP_LOOKUPS

from .models import Post


class PostFilter(django_filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            "title": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "member": ["exact", "in"],
            "created_at": TIMESTAMP_LOOKUPS,
            "updated_at": TIMESTAMP_LOOKUPS,
        }
