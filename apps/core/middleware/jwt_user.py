"""
Lightweight JWT user middleware for observability.

Extracts user_id from JWT token and sets a lightweight user object on request
for django_structlog logging. Does NOT query the database.
This is NOT a security boundary -- DRF's JWTAuthentication handles actual auth.
Falls back to AnonymousUser on any error (missing header, invalid token, etc.).
"""

import logging

import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class _JWTUser:
    """Lightweight user stand-in for structlog. No DB query."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, user_id):
        self.id = user_id
        self.pk = user_id

    def __str__(self):
        return f"User(id={self.id})"


class JWTUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = self._get_user_from_jwt(request)
        return self.get_response(request)

    def _get_user_from_jwt(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return AnonymousUser()

        token = auth_header[7:]
        try:
            conf = settings.JWT_AUTH
            payload = jwt.decode(
                token,
                conf["SIGNING_KEY"],
                algorithms=[conf["ALGORITHM"]],
                options={"verify_exp": False},
            )
            user_id = payload.get("user_id")
            if not user_id:
                return AnonymousUser()
            return _JWTUser(user_id)
        except Exception:
            return AnonymousUser()
