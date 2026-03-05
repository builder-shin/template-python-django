"""
Lightweight JWT user middleware for observability.

Sets request.user from JWT token for django_structlog logging purposes.
This is NOT a security boundary -- DRF's JWTAuthentication handles actual auth.
Falls back to AnonymousUser on any error (missing header, invalid token, etc.).
"""

import logging

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)
UserModel = get_user_model()


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
            )
            jti = payload.get("jti")
            if not jti:
                return AnonymousUser()
            from apps.core.auth.token_store import TokenStore

            if not TokenStore.is_token_valid(jti):
                return AnonymousUser()
            return UserModel.objects.get(id=payload["user_id"])
        except Exception:
            return AnonymousUser()
