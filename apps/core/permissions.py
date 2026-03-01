from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.conf import settings

from apps.core.utils import get_client_ip


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "id") or request.user.id is None:
            raise NotAuthenticated("로그인 후 이용해주세요.")
        return True


class IsEnterprise(BasePermission):
    def has_permission(self, request, view):
        IsAuthenticated().has_permission(request, view)
        if not request.user.is_enterprise():
            raise PermissionDenied("기업 회원만 이용 가능합니다.")
        return True


class IsPersonal(BasePermission):
    def has_permission(self, request, view):
        IsAuthenticated().has_permission(request, view)
        if not request.user.is_personal():
            raise PermissionDenied("개인 회원만 이용 가능합니다.")
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
