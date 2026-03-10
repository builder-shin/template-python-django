import pytest
from django.core.cache import cache
from django.test import RequestFactory, override_settings

from apps.core.middleware.allow2ban import Allow2BanMiddleware


@pytest.fixture(autouse=True)
def clear_cache():
    """테스트 간 캐시 격리."""
    cache.clear()
    yield
    cache.clear()


def _make_middleware(response_value=None):
    """테스트용 미들웨어 인스턴스 생성."""
    return Allow2BanMiddleware(lambda request: response_value or "OK")


class TestAllow2BanBlocking:
    def test_static_blocklist_returns_403(self):
        """settings.BLOCKED_IPS에 포함된 IP는 403 반환."""
        middleware = _make_middleware()
        factory = RequestFactory()
        request = factory.get("/api/v1/posts")
        request.META["REMOTE_ADDR"] = "1.2.3.4"

        with override_settings(BLOCKED_IPS=["1.2.3.4"]):
            response = middleware(request)

        assert response.status_code == 403
        assert "application/vnd.api+json" in response["Content-Type"]

    def test_dynamically_banned_ip_returns_403(self):
        """캐시에 ban 플래그가 있는 IP는 403 반환."""
        middleware = _make_middleware()
        factory = RequestFactory()
        request = factory.get("/api/v1/posts")
        request.META["REMOTE_ADDR"] = "5.6.7.8"

        cache.set("allow2ban:banned:5.6.7.8", True, 60)

        response = middleware(request)
        assert response.status_code == 403

    def test_clean_ip_passes_through(self):
        """차단되지 않은 IP는 정상 통과."""
        middleware = _make_middleware(response_value="OK")
        factory = RequestFactory()
        request = factory.get("/api/v1/posts")
        request.META["REMOTE_ADDR"] = "10.0.0.1"

        response = middleware(request)
        assert response == "OK"


class TestAllow2BanSuspiciousTracking:
    def test_suspicious_path_records_hit(self):
        """의심스러운 경로 접근 시 카운트 증가."""
        middleware = _make_middleware(response_value="OK")
        factory = RequestFactory()
        request = factory.get("/wp-admin/login")
        request.META["REMOTE_ADDR"] = "10.0.0.2"

        middleware(request)

        count = cache.get("allow2ban:count:10.0.0.2")
        assert count == 1

    def test_auto_ban_after_max_retry(self):
        """MAX_RETRY 초과 시 자동 ban."""
        middleware = _make_middleware(response_value="OK")
        factory = RequestFactory()

        for _ in range(Allow2BanMiddleware.MAX_RETRY):
            request = factory.get("/.env")
            request.META["REMOTE_ADDR"] = "10.0.0.3"
            middleware(request)

        assert cache.get("allow2ban:banned:10.0.0.3") is True
        # 카운트 키는 ban 후 삭제됨
        assert cache.get("allow2ban:count:10.0.0.3") is None

    def test_banned_ip_blocked_on_next_request(self):
        """자동 ban 이후 다음 요청은 403."""
        middleware = _make_middleware(response_value="OK")
        factory = RequestFactory()

        # MAX_RETRY까지 의심스러운 요청
        for _ in range(Allow2BanMiddleware.MAX_RETRY):
            request = factory.get("/phpmyadmin")
            request.META["REMOTE_ADDR"] = "10.0.0.4"
            middleware(request)

        # 다음 요청은 403
        request = factory.get("/api/v1/posts")
        request.META["REMOTE_ADDR"] = "10.0.0.4"
        response = middleware(request)
        assert response.status_code == 403
