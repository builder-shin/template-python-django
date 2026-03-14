import os

from .base import *  # noqa: F403

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

JWT_AUTH = globals().get("JWT_AUTH", {})
JWT_AUTH["SIGNING_KEY"] = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)

DEBUG = False

# SSL / Proxy (Railway terminates SSL at reverse proxy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Health check path exclusion from SSL redirect
SECURE_REDIRECT_EXEMPT = [r"^health/"]

# Security headers
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
