from apps.core.filters import create_ransack_filterset
from .models import Post

PostFilter = create_ransack_filterset(
    Post,
    ["title", "status", "created_at", "updated_at", "user_id"],
)
