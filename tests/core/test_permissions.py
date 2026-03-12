from django.test import RequestFactory

from apps.core.permissions import IsOwnerOrReadOnly


class TestIsOwnerOrReadOnly:
    def _make_request(self, method="GET"):
        factory = RequestFactory()
        return getattr(factory, method.lower())("/")

    def test_get_request_always_allowed(self):
        perm = IsOwnerOrReadOnly()
        request = self._make_request("GET")
        obj = type("Obj", (), {"user_id": 999})()
        request.user = type("User", (), {"id": 1})()
        assert perm.has_object_permission(request, None, obj) is True

    def test_head_request_always_allowed(self):
        perm = IsOwnerOrReadOnly()
        request = self._make_request("HEAD")
        obj = type("Obj", (), {"user_id": 999})()
        request.user = type("User", (), {"id": 1})()
        assert perm.has_object_permission(request, None, obj) is True

    def test_owner_can_patch(self):
        perm = IsOwnerOrReadOnly()
        request = self._make_request("PATCH")
        request.user = type("User", (), {"id": 42})()
        obj = type("Obj", (), {"user_id": 42})()
        assert perm.has_object_permission(request, None, obj) is True

    def test_non_owner_cannot_patch(self):
        perm = IsOwnerOrReadOnly()
        request = self._make_request("PATCH")
        request.user = type("User", (), {"id": 1})()
        obj = type("Obj", (), {"user_id": 42})()
        assert perm.has_object_permission(request, None, obj) is False
