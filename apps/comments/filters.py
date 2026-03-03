import django_filters

from apps.core.filters import TIMESTAMP_LOOKUPS

from .models import Comment


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            "content": ["exact", "icontains"],
            "member": ["exact", "in"],
            "post": ["exact", "in"],
            "parent": ["exact", "isnull"],
            "created_at": TIMESTAMP_LOOKUPS,
            "updated_at": TIMESTAMP_LOOKUPS,
        }
