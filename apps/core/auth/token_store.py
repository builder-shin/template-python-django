"""
Redis-backed token store using Django cache framework.

Stores:
  - jti:{jti} -> {"user_id": int, "type": "access"|"refresh"}, TTL = token lifetime
  - user_tokens:{user_id} -> JSON list of active jti strings, TTL = refresh lifetime + 1h

Race condition note (accepted trade-off):
  user_tokens list의 동시 수정은 같은 유저가 동시에 login/logout하는 극히 드문 경우에만 발생.
  최악의 경우 jti 하나가 list에서 누락되는 정도 -- TTL 기반 jti 만료가 안전장치 역할.
"""

import json

from django.core.cache import cache


class TokenStore:
    JTI_PREFIX = "jti:"
    USER_TOKENS_PREFIX = "user_tokens:"

    @classmethod
    def _user_tokens_ttl(cls) -> int:
        """TTL for user_tokens list: refresh token lifetime + 1 hour buffer."""
        from django.conf import settings as django_settings

        return django_settings.JWT_AUTH.get("REFRESH_TOKEN_LIFETIME_SECONDS", 604800) + 3600

    @classmethod
    def store_token(cls, jti: str, user_id: int, token_type: str, ttl: int) -> None:
        """토큰 저장. jti 키에 메타정보, user_tokens에 jti 추가."""
        cache.set(
            f"{cls.JTI_PREFIX}{jti}",
            {"user_id": user_id, "type": token_type},
            ttl,
        )
        cls._add_to_user_tokens(user_id, jti)

    @classmethod
    def is_token_valid(cls, jti: str) -> bool:
        """jti가 캐시에 존재하는지 확인."""
        return cache.get(f"{cls.JTI_PREFIX}{jti}") is not None

    @classmethod
    def get_token_data(cls, jti: str) -> dict | None:
        """jti의 메타정보 반환. 없으면 None."""
        return cache.get(f"{cls.JTI_PREFIX}{jti}")

    @classmethod
    def revoke_token(cls, jti: str) -> None:
        """단일 토큰 무효화."""
        data = cache.get(f"{cls.JTI_PREFIX}{jti}")
        cache.delete(f"{cls.JTI_PREFIX}{jti}")
        if data and "user_id" in data:
            cls._remove_from_user_tokens(data["user_id"], jti)

    @classmethod
    def atomic_revoke(cls, jti: str) -> bool:
        """Atomically check and revoke. Returns True if token was valid and is now revoked."""
        key = f"{cls.JTI_PREFIX}{jti}"
        data = cache.get(key)
        if data is None:
            return False
        cache.delete(key)
        if data and isinstance(data, dict) and "user_id" in data:
            cls._remove_from_user_tokens(data["user_id"], jti)
        return True

    @classmethod
    def revoke_all_user_tokens(cls, user_id: int) -> None:
        """사용자의 모든 활성 토큰 무효화. cache.delete_many()로 일괄 삭제."""
        user_key = f"{cls.USER_TOKENS_PREFIX}{user_id}"
        raw = cache.get(user_key)
        if raw:
            jti_list = json.loads(raw) if isinstance(raw, str) else raw
            jti_keys = [f"{cls.JTI_PREFIX}{jti}" for jti in jti_list]
            if jti_keys:
                cache.delete_many(jti_keys)
        cache.delete(user_key)

    @classmethod
    def _add_to_user_tokens(cls, user_id: int, jti: str) -> None:
        user_key = f"{cls.USER_TOKENS_PREFIX}{user_id}"
        raw = cache.get(user_key)
        jti_list = json.loads(raw) if isinstance(raw, str) else (raw or [])
        # Lazy prune using batch check (reduce N Redis calls to 1)
        if len(jti_list) > 10:  # Only prune when list is large enough to matter
            jti_keys = [f"{cls.JTI_PREFIX}{j}" for j in jti_list]
            valid_map = cache.get_many(jti_keys)
            jti_list = [j for j in jti_list if f"{cls.JTI_PREFIX}{j}" in valid_map]
        if jti not in jti_list:
            jti_list.append(jti)
        cache.set(user_key, json.dumps(jti_list), cls._user_tokens_ttl())

    @classmethod
    def _remove_from_user_tokens(cls, user_id: int, jti: str) -> None:
        user_key = f"{cls.USER_TOKENS_PREFIX}{user_id}"
        raw = cache.get(user_key)
        if not raw:
            return
        jti_list = json.loads(raw) if isinstance(raw, str) else raw
        jti_list = [j for j in jti_list if j != jti]
        if jti_list:
            cache.set(user_key, json.dumps(jti_list), cls._user_tokens_ttl())
        else:
            cache.delete(user_key)
