import django_filters

from .models import Comment


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            "content": ["exact", "icontains"],
            "user_id": ["exact", "in"],
            "post": ["exact", "in"],
            "parent": ["exact", "isnull"],
            "created_at": ["exact", "gt", "gte", "lt", "lte"],
            "updated_at": ["exact", "gt", "gte", "lt", "lte"],
        }
