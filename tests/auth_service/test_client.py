import time

import httpx
import pytest
import respx

from apps.auth_service.client import (
    AuthServiceClient,
    AuthenticationError,
    CircuitBreaker,
    CircuitOpenError,
    ServiceUnavailableError,
    _circuit_breaker,
)
from apps.auth_service.models import AuthUser


@pytest.fixture(autouse=True)
def reset_circuit():
    """Reset circuit breaker before each test."""
    AuthServiceClient.reset_circuit()
    yield
    AuthServiceClient.reset_circuit()


@pytest.fixture
def auth_response_data():
    return {
        "success": True,
        "data": {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "workspace_id": "ws-456",
            "workspace_kind": "personal",
            "workspace_role": "owner",
            "member_status": "active",
        },
    }


class TestAuthServiceClient:
    @respx.mock
    def test_successful_auth(self, settings, auth_response_data):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(200, json=auth_response_data)
        )
        client = AuthServiceClient()
        user = client.verify_session("valid-token")
        assert user is not None
        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.workspace_id == "ws-456"
        assert user.workspace_kind == "personal"
        assert user.workspace_role == "owner"
        assert user.member_status == "active"

    @respx.mock
    def test_auth_user_methods(self, settings, auth_response_data):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(200, json=auth_response_data)
        )
        client = AuthServiceClient()
        user = client.verify_session("valid-token")
        assert user.is_personal() is True
        assert user.is_enterprise() is False
        assert user.is_authenticated is True
        assert user.is_anonymous is False

    @respx.mock
    def test_enterprise_user(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        data = {
            "success": True,
            "data": {
                "id": "user-789",
                "email": "enterprise@example.com",
                "name": "Enterprise User",
                "workspace_id": "ws-ent",
                "workspace_kind": "enterprise",
                "workspace_role": "admin",
                "member_status": "active",
            },
        }
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(200, json=data)
        )
        client = AuthServiceClient()
        user = client.verify_session("enterprise-token")
        assert user.is_enterprise() is True
        assert user.is_personal() is False

    @respx.mock
    def test_response_caching(self, settings, auth_response_data):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 300
        route = respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(200, json=auth_response_data)
        )
        client = AuthServiceClient()
        user1 = client.verify_session("cached-token")
        user2 = client.verify_session("cached-token")
        assert user1 is not None
        assert user2 is not None
        assert route.call_count == 1

    @respx.mock
    def test_401_raises_authentication_error(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )
        client = AuthServiceClient()
        with pytest.raises(AuthenticationError):
            client.verify_session("invalid-token")

    @respx.mock
    def test_500_raises_service_unavailable(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(500, json={"error": "Internal Server Error"})
        )
        client = AuthServiceClient()
        with pytest.raises(ServiceUnavailableError):
            client.verify_session("some-token")

    @respx.mock
    def test_timeout_raises_service_unavailable(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            side_effect=httpx.ConnectTimeout("Connection timed out")
        )
        client = AuthServiceClient()
        with pytest.raises(ServiceUnavailableError):
            client.verify_session("some-token")

    @respx.mock
    def test_connect_error_raises_service_unavailable(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        client = AuthServiceClient()
        with pytest.raises(ServiceUnavailableError):
            client.verify_session("some-token")

    @respx.mock
    def test_success_false_returns_none(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(200, json={"success": False, "data": None})
        )
        client = AuthServiceClient()
        user = client.verify_session("some-token")
        assert user is None


class TestCircuitBreaker:
    def test_starts_closed(self):
        cb = CircuitBreaker()
        assert cb.is_open() is False

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker()
        for _ in range(CircuitBreaker.FAILURE_THRESHOLD):
            cb.record_failure()
        assert cb.is_open() is True

    def test_resets_on_success(self):
        cb = CircuitBreaker()
        for _ in range(3):
            cb.record_failure()
        cb.record_success()
        assert cb.is_open() is False

    def test_reset_method(self):
        cb = CircuitBreaker()
        for _ in range(CircuitBreaker.FAILURE_THRESHOLD):
            cb.record_failure()
        assert cb.is_open() is True
        cb.reset()
        assert cb.is_open() is False

    @respx.mock
    def test_circuit_open_raises_error(self, settings):
        settings.AUTH_SERVICE_URL = "http://localhost:3001"
        settings.AUTH_SESSION_CACHE_TTL = 0
        respx.get("http://localhost:3001/api/auth/me").mock(
            return_value=httpx.Response(500, json={"error": "fail"})
        )
        client = AuthServiceClient()
        for _ in range(CircuitBreaker.FAILURE_THRESHOLD):
            try:
                client.verify_session(f"token-{_}")
            except ServiceUnavailableError:
                pass
        with pytest.raises(CircuitOpenError):
            client.verify_session("another-token")
