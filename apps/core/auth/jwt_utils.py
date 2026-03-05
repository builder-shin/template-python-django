"""
JWT token generation and verification utilities.
Uses PyJWT for encoding/decoding, TokenStore for Redis-backed validation.
"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.core.auth.token_store import TokenStore

User = get_user_model()


def _get_jwt_settings():
    return settings.JWT_AUTH


def generate_token_pair(user) -> dict:
    """
    Generate access + refresh token pair for user.
    Returns: {"access": str, "refresh": str}
    """
    conf = _get_jwt_settings()
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)  # noqa: UP017 - freezegun doesn't support datetime.UTC

    access_payload = {
        "jti": access_jti,
        "user_id": user.id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=conf["ACCESS_TOKEN_LIFETIME_SECONDS"]),
    }
    refresh_payload = {
        "jti": refresh_jti,
        "user_id": user.id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=conf["REFRESH_TOKEN_LIFETIME_SECONDS"]),
    }

    access_token = jwt.encode(access_payload, conf["SIGNING_KEY"], algorithm=conf["ALGORITHM"])
    refresh_token = jwt.encode(refresh_payload, conf["SIGNING_KEY"], algorithm=conf["ALGORITHM"])

    TokenStore.store_token(access_jti, user.id, "access", conf["ACCESS_TOKEN_LIFETIME_SECONDS"])
    TokenStore.store_token(refresh_jti, user.id, "refresh", conf["REFRESH_TOKEN_LIFETIME_SECONDS"])

    return {"access": access_token, "refresh": refresh_token}


def decode_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode and validate JWT token.
    Checks: signature, expiry, type, Redis jti existence.
    Returns payload dict on success.
    Raises: jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError (revoked/wrong type)
    """
    conf = _get_jwt_settings()
    payload = jwt.decode(token, conf["SIGNING_KEY"], algorithms=[conf["ALGORITHM"]])

    if payload.get("type") != expected_type:
        raise ValueError(f"Expected {expected_type} token, got {payload.get('type')}")

    jti = payload.get("jti")
    if not jti or not TokenStore.is_token_valid(jti):
        raise ValueError("Token has been revoked")

    return payload


def refresh_access_token(refresh_token_str: str) -> dict:
    """
    Rotate: validate refresh token -> atomically revoke old refresh -> issue new pair.
    Returns: {"access": str, "refresh": str}
    Raises: jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError
    """
    payload = decode_token(refresh_token_str, expected_type="refresh")

    # Atomic revoke: only proceed if we were the one to revoke it
    if not TokenStore.atomic_revoke(payload["jti"]):
        raise ValueError("Token has already been used")

    user = User.objects.get(id=payload["user_id"])
    return generate_token_pair(user)
