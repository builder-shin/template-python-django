import django_filters

from .models import Post


class PostFilter(django_filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            "title": ["exact", "icontains", "istartswith", "iendswith"],
            "status": ["exact", "in"],
            "user_id": ["exact", "in"],
            "created_at": ["exact", "gt", "gte", "lt", "lte"],
            "updated_at": ["exact", "gt", "gte", "lt", "lte"],
        }
