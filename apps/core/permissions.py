from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: only the owner can mutate (PUT/PATCH/DELETE).
    Assumes the object has a `user_id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return hasattr(obj, "user_id") and obj.user_id == request.user.id
