import logging

from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)

_SENTINEL = object()


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission: only the owner can mutate (PUT/PATCH/DELETE).

    Set ``owner_field`` on the view to customize which attribute is compared
    to ``request.user.id``. Default: ``"user_id"`` (FK-based ownership).
    For User model, set ``owner_field = "id"`` (user owns themselves).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        owner_field = getattr(view, "owner_field", "user_id")
        obj_owner = getattr(obj, owner_field, _SENTINEL)
        if obj_owner is _SENTINEL:
            raise ImproperlyConfigured(f"IsOwnerOrReadOnly: field '{owner_field}' not found on {type(obj).__name__}")
        return obj_owner == request.user.id
