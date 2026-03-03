from rest_framework.throttling import SimpleRateThrottle

from apps.core.utils import get_client_ip


class AuthRateThrottle(SimpleRateThrottle):
    scope = "auth"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": get_client_ip(request),
        }
