from .base import *  # noqa: F401,F403

DEBUG = False

# SSL / Proxy (Railway terminates SSL at reverse proxy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Health check path exclusion from SSL redirect
SECURE_REDIRECT_EXEMPT = [r"^health/"]
