from apps.core.filters import create_ransack_filterset
from .models import Member

MemberFilter = create_ransack_filterset(
    Member,
    ["nickname", "status", "user_id", "created_at", "updated_at"],
)
