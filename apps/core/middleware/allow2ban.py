import logging

from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class Allow2BanMiddleware:
    """
    Dynamic IP auto-ban middleware equivalent to Rails Rack::Attack Allow2Ban.
    Automatically bans IPs that make suspicious requests (path scanning attacks).

    Uses Django cache (Redis in production) for state storage.

    Configuration:
    - SUSPICIOUS_PATTERNS: paths that trigger ban tracking
    - MAX_RETRY: max suspicious hits before ban (default: 20)
    - FIND_TIME: window in seconds to count hits (default: 60)
    - BAN_TIME: ban duration in seconds (default: 3600)
    """

    SUSPICIOUS_PATTERNS = [
        "/etc/passwd",
        "wp-admin",
        "wp-login",
        ".env",
        "phpinfo",
        "phpmyadmin",
    ]
    MAX_RETRY = 20
    FIND_TIME = 60  # seconds
    BAN_TIME = 3600  # seconds (1 hour)

    CACHE_PREFIX_BAN = "allow2ban:banned:"
    CACHE_PREFIX_COUNT = "allow2ban:count:"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_client_ip(request)

        # Check if IP is banned
        if cache.get(f"{self.CACHE_PREFIX_BAN}{ip}"):
            logger.warning(f"Blocked banned IP: {ip}")
            return JsonResponse(
                {
                    "errors": [
                        {
                            "status": "403",
                            "title": "Forbidden",
                            "detail": "접근이 차단되었습니다.",
                        }
                    ]
                },
                status=403,
                content_type="application/vnd.api+json",
            )

        # Check if request path matches suspicious patterns
        path = request.path.lower()
        if any(pattern in path for pattern in self.SUSPICIOUS_PATTERNS):
            self._record_suspicious_hit(ip)

        return self.get_response(request)

    def _record_suspicious_hit(self, ip):
        """Record a suspicious hit and ban if threshold exceeded."""
        cache_key = f"{self.CACHE_PREFIX_COUNT}{ip}"
        count = cache.get(cache_key, 0)
        count += 1
        cache.set(cache_key, count, self.FIND_TIME)

        if count >= self.MAX_RETRY:
            # Ban the IP
            cache.set(f"{self.CACHE_PREFIX_BAN}{ip}", True, self.BAN_TIME)
            cache.delete(cache_key)
            logger.warning(
                f"Auto-banned IP {ip} for {self.BAN_TIME}s "
                f"after {count} suspicious requests"
            )

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
