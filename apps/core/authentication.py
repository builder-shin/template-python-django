"""
JWT Authentication backend for Django REST Framework.
Validates Bearer tokens via signature verification + Redis jti check.
"""
import logging

import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.core.auth.jwt_utils import decode_token

User = get_user_model()

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    DRF authentication backend.
    Expects: Authorization: Bearer <access_token>
    Returns: (user, payload) tuple on success.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None  # No JWT auth attempted -- let other backends try

        token = auth_header[len(self.keyword) + 1:]

        try:
            payload = decode_token(token, expected_type="access")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.") from None
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.") from None
        except ValueError as e:
            raise AuthenticationFailed(str(e)) from None

        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.") from None

        if user.status != User.Status.ACTIVE:
            raise AuthenticationFailed("User account is disabled.")

        return (user, payload)

    def authenticate_header(self, request):
        return self.keyword
