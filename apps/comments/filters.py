from apps.core.filters import create_ransack_filterset
from .models import Comment

CommentFilter = create_ransack_filterset(
    Comment,
    ["content", "user_id", "post", "parent", "created_at", "updated_at"],
)
