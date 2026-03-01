from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.conf import settings

from apps.core.utils import get_client_ip


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("로그인 후 이용해주세요.")
        return True


class IPBlocklistPermission(BasePermission):
    """
    Equivalent to Rails rack-attack blocklist.
    Checks request IP against a configurable blocklist.
    Configure via settings.BLOCKED_IPS (list of IP strings).
    """

    def has_permission(self, request, view):
        blocked_ips = getattr(settings, "BLOCKED_IPS", [])
        if not blocked_ips:
            return True
        client_ip = get_client_ip(request)
        if client_ip in blocked_ips:
            raise PermissionDenied("접근이 차단되었습니다.")
        return True
