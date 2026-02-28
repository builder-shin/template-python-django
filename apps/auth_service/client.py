import hashlib
import threading
import time
from typing import Optional

import httpx
from django.conf import settings
from django.core.cache import cache

from .models import AuthUser


class AuthenticationError(Exception):
    pass


class ServiceUnavailableError(Exception):
    pass


class CircuitOpenError(ServiceUnavailableError):
    pass


class CircuitBreaker:
    """Thread-safe circuit breaker. Process-local state (same as Rails Puma workers)."""

    FAILURE_THRESHOLD = 5
    RESET_TIMEOUT = 30  # seconds

    def __init__(self):
        self._lock = threading.Lock()
        self._state = "closed"
        self._failure_count = 0
        self._last_failure_at = None

    def record_success(self):
        with self._lock:
            self._state = "closed"
            self._failure_count = 0
            self._last_failure_at = None

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_at = time.time()
            if self._failure_count >= self.FAILURE_THRESHOLD:
                self._state = "open"

    def is_open(self) -> bool:
        with self._lock:
            if self._state == "closed":
                return False
            if self._state == "open":
                if self._last_failure_at and (time.time() - self._last_failure_at) >= self.RESET_TIMEOUT:
                    self._state = "half_open"
                    return False
                return True
            return False  # half_open allows requests

    def reset(self):
        with self._lock:
            self._state = "closed"
            self._failure_count = 0
            self._last_failure_at = None


# Module-level circuit breaker (shared across instances, process-local)
_circuit_breaker = CircuitBreaker()


# Module-level shared HTTP client (connection pooling, process-local)
_http_client = None
_http_client_lock = threading.Lock()


def _get_http_client() -> httpx.Client:
    """Lazily create and return a shared httpx.Client for connection pooling."""
    global _http_client
    if _http_client is None:
        with _http_client_lock:
            if _http_client is None:
                base_url = getattr(settings, "AUTH_SERVICE_URL", "http://localhost:3001")
                timeout = getattr(settings, "AUTH_REQUEST_TIMEOUT", 5)
                _http_client = httpx.Client(
                    base_url=base_url,
                    timeout=timeout,
                )
    return _http_client


class AuthServiceClient:
    RETRY_STATUS_CODES = {502, 503, 504}
    MAX_RETRIES = 2
    RETRY_INTERVAL = 0.1  # seconds

    def __init__(self):
        self._base_url = getattr(settings, "AUTH_SERVICE_URL", "http://localhost:3001")
        self._cache_ttl = getattr(settings, "AUTH_SESSION_CACHE_TTL", 300)
        self._timeout = getattr(settings, "AUTH_REQUEST_TIMEOUT", 5)

    def verify_session(self, bearer_token: str) -> Optional[AuthUser]:
        if _circuit_breaker.is_open():
            raise CircuitOpenError("인증 서비스가 일시적으로 이용 불가합니다. 잠시 후 다시 시도해주세요.")

        cache_key = f"auth:session:{hashlib.sha256(bearer_token.encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        user = self._fetch_user_from_auth_service(bearer_token)
        if user is not None:
            cache.set(cache_key, user, self._cache_ttl)
        return user

    def _fetch_user_from_auth_service(self, bearer_token: str) -> Optional[AuthUser]:
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                client = _get_http_client()
                response = client.get(
                    "/api/auth/me",
                    cookies={"session_web": bearer_token},
                )

                if response.status_code == 200:
                    _circuit_breaker.record_success()
                    return self._parse_user_response(response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("인증에 실패했습니다.")
                elif response.status_code in self.RETRY_STATUS_CODES and attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_INTERVAL)
                    continue
                else:
                    _circuit_breaker.record_failure()
                    raise ServiceUnavailableError("인증 서비스에 연결할 수 없습니다.")

            except (httpx.TimeoutException, httpx.ConnectError):
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_INTERVAL)
                    continue
                _circuit_breaker.record_failure()
                raise ServiceUnavailableError("인증 서비스에 연결할 수 없습니다.")

        _circuit_breaker.record_failure()
        raise ServiceUnavailableError("인증 서비스에 연결할 수 없습니다.")

    def _parse_user_response(self, body: dict) -> Optional[AuthUser]:
        if not body.get("success") or not body.get("data"):
            return None
        data = body["data"]
        return AuthUser(
            id=data.get("id"),
            email=data.get("email"),
            name=data.get("name"),
            workspace_id=data.get("workspace_id"),
            workspace_kind=data.get("workspace_kind"),
            workspace_role=data.get("workspace_role"),
            member_status=data.get("member_status"),
        )

    @classmethod
    def reset_circuit(cls):
        _circuit_breaker.reset()

    @classmethod
    def reset_client(cls):
        global _http_client
        with _http_client_lock:
            if _http_client is not None:
                _http_client.close()
                _http_client = None
