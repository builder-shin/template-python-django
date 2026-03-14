import jwt as pyjwt
import pytest
from django.conf import settings
from freezegun import freeze_time

from apps.core.auth.jwt_utils import generate_token_pair
from apps.core.auth.token_store import TokenStore


@pytest.mark.django_db
class TestLogin:
    """POST /api/v1/auth/login"""

    def test_login_success(self, api_client, auth_user):
        """올바른 credentials -> 200 + token pair"""
        response = api_client.post(
            "/api/v1/auth/login", {"email": auth_user.email, "password": "testpass123"}, content_type="application/json"
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, auth_user):
        """잘못된 password -> 401"""
        response = api_client.post(
            "/api/v1/auth/login", {"email": auth_user.email, "password": "wrong"}, content_type="application/json"
        )
        assert response.status_code == 401

    def test_login_nonexistent_email(self, api_client):
        """존재하지 않는 email -> 401"""
        response = api_client.post(
            "/api/v1/auth/login", {"email": "nobody@example.com", "password": "any"}, content_type="application/json"
        )
        assert response.status_code == 401

    def test_login_suspended_user(self, api_client, auth_user):
        """비활성 사용자 -> 403"""
        auth_user.status = auth_user.Status.SUSPENDED
        auth_user.save()
        response = api_client.post(
            "/api/v1/auth/login", {"email": auth_user.email, "password": "testpass123"}, content_type="application/json"
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestTokenValidation:
    """Access token 검증"""

    def test_valid_access_token(self, jwt_authenticated_client):
        """유효한 access token -> 인증 성공 (아무 protected endpoint)"""
        response = jwt_authenticated_client.get("/api/v1/users/me")
        assert response.status_code == 200

    def test_expired_access_token(self, api_client, auth_user):
        """만료된 access token -> 401"""
        with freeze_time("2020-01-01"):
            tokens = generate_token_pair(auth_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = api_client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_tampered_token(self, api_client):
        """변조된 token -> 401"""
        api_client.credentials(HTTP_AUTHORIZATION="Bearer eyJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoiZmFrZSJ9.fake_sig")
        response = api_client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_revoked_token(self, api_client, auth_user, auth_tokens):
        """Redis에서 삭제된 jti -> 401"""
        access = auth_tokens["access"]
        payload = pyjwt.decode(access, settings.JWT_AUTH["SIGNING_KEY"], algorithms=["HS256"])
        TokenStore.revoke_token(payload["jti"])
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_no_auth_header(self, api_client):
        """인증 헤더 없음 -> 401 (IsAuthenticated permission)"""
        response = api_client.get("/api/v1/users/me")
        assert response.status_code == 401


@pytest.mark.django_db
class TestRefresh:
    """POST /api/v1/auth/refresh"""

    def test_refresh_success(self, api_client, auth_tokens):
        """유효한 refresh -> 새 token pair"""
        response = api_client.post(
            "/api/v1/auth/refresh", {"refresh": auth_tokens["refresh"]}, content_type="application/json"
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["access"] != auth_tokens["access"]
        assert response.data["refresh"] != auth_tokens["refresh"]

    def test_refresh_rotation_invalidates_old(self, api_client, auth_tokens):
        """사용된 refresh (rotation 후) -> 401"""
        api_client.post("/api/v1/auth/refresh", {"refresh": auth_tokens["refresh"]}, content_type="application/json")
        response = api_client.post(
            "/api/v1/auth/refresh", {"refresh": auth_tokens["refresh"]}, content_type="application/json"
        )
        assert response.status_code == 401

    def test_refresh_expired(self, api_client, auth_user):
        """만료된 refresh -> 401"""
        with freeze_time("2020-01-01"):
            tokens = generate_token_pair(auth_user)
        response = api_client.post(
            "/api/v1/auth/refresh", {"refresh": tokens["refresh"]}, content_type="application/json"
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestLogout:
    """POST /api/v1/auth/logout, /api/v1/auth/logout-all"""

    def test_logout_revokes_access(self, jwt_authenticated_client, access_token):
        """로그아웃 후 access token -> 401"""
        response = jwt_authenticated_client.post("/api/v1/auth/logout")
        assert response.status_code == 204
        response = jwt_authenticated_client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_logout_all_revokes_all_sessions(self, api_client, auth_user):
        """logout-all 후 모든 세션 -> 401"""
        tokens1 = generate_token_pair(auth_user)
        tokens2 = generate_token_pair(auth_user)

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens1['access']}")
        response = api_client.post("/api/v1/auth/logout-all")
        assert response.status_code == 204

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens1['access']}")
        assert api_client.get("/api/v1/users/me").status_code == 401

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens2['access']}")
        assert api_client.get("/api/v1/users/me").status_code == 401


@pytest.mark.django_db
class TestLogoutWithRefresh:
    """Logout with refresh token in body (covers views.py:88-94)."""

    def test_logout_with_refresh_revokes_both(self, api_client, auth_user):
        tokens = generate_token_pair(auth_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = api_client.post(
            "/api/v1/auth/logout", {"refresh": tokens["refresh"]}, content_type="application/json"
        )
        assert response.status_code == 204
        refresh_jti = pyjwt.decode(tokens["refresh"], options={"verify_signature": False})["jti"]
        assert TokenStore.is_token_valid(refresh_jti) is False


@pytest.mark.django_db
class TestAuthenticationEdgeCases:
    """authentication.py edge cases: user not found, disabled user."""

    def test_deleted_user_returns_401(self, api_client, auth_user):
        """토큰은 유효하지만 유저가 삭제된 경우 → 401."""
        tokens = generate_token_pair(auth_user)
        auth_user.delete()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = api_client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_suspended_user_returns_401(self, api_client, auth_user):
        """유저가 정지된 경우 → 401."""
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        tokens = generate_token_pair(auth_user)
        auth_user.status = user_model.Status.SUSPENDED
        auth_user.save()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = api_client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestTokenStore:
    """TokenStore unit tests (직접 LocMemCache에서 동작 확인 -- DB 불필요)"""

    def test_store_and_validate(self):
        TokenStore.store_token("test-jti", 999, "access", 900)
        assert TokenStore.is_token_valid("test-jti") is True

    def test_revoke_single(self):
        TokenStore.store_token("rev-jti", 999, "access", 900)
        TokenStore.revoke_token("rev-jti")
        assert TokenStore.is_token_valid("rev-jti") is False

    def test_revoke_all_user(self):
        TokenStore.store_token("u1-jti-1", 100, "access", 900)
        TokenStore.store_token("u1-jti-2", 100, "refresh", 2592000)
        TokenStore.revoke_all_user_tokens(100)
        assert TokenStore.is_token_valid("u1-jti-1") is False
        assert TokenStore.is_token_valid("u1-jti-2") is False

    def test_get_token_data(self):
        """get_token_data returns stored metadata."""
        TokenStore.store_token("data-jti", 42, "access", 900)
        data = TokenStore.get_token_data("data-jti")
        assert data is not None
        assert data["user_id"] == 42

    def test_get_token_data_missing(self):
        """get_token_data returns None for missing jti."""
        assert TokenStore.get_token_data("nonexistent-jti") is None

    def test_revoke_if_valid_success(self):
        """revoke_if_valid returns True for valid token."""
        TokenStore.store_token("atomic-jti", 42, "access", 900)
        assert TokenStore.revoke_if_valid("atomic-jti") is True
        assert TokenStore.is_token_valid("atomic-jti") is False

    def test_revoke_if_valid_missing(self):
        """revoke_if_valid returns False for nonexistent token."""
        assert TokenStore.revoke_if_valid("missing-jti") is False
