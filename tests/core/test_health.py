import json
from unittest.mock import patch

import pytest
from django.test import RequestFactory

from apps.core.views import health_live, health_ready


class TestHealthLive:
    def test_returns_200_ok(self):
        factory = RequestFactory()
        request = factory.get("/health/live")
        response = health_live(request)
        assert response.status_code == 200
        assert response.content == b"OK"


@pytest.mark.django_db
class TestHealthReady:
    def test_returns_200_when_all_healthy(self):
        factory = RequestFactory()
        request = factory.get("/health/ready")
        response = health_ready(request)
        assert response.status_code == 200
        assert response.content == b"OK"

    def test_returns_503_when_db_unavailable(self):
        factory = RequestFactory()
        request = factory.get("/health/ready")

        with patch("apps.core.views.connection") as mock_conn:
            mock_conn.ensure_connection.side_effect = Exception("DB down")
            response = health_ready(request)

        assert response.status_code == 503
        data = json.loads(response.content)
        assert "DB: unavailable" in data["errors"]

    def test_returns_503_when_cache_unavailable(self):
        factory = RequestFactory()
        request = factory.get("/health/ready")

        with patch("apps.core.views.cache") as mock_cache:
            mock_cache.set.side_effect = Exception("Cache down")
            response = health_ready(request)

        assert response.status_code == 503
        data = json.loads(response.content)
        assert "Cache: unavailable" in data["errors"]

    def test_returns_503_when_cache_returns_wrong_value(self):
        factory = RequestFactory()
        request = factory.get("/health/ready")

        with patch("apps.core.views.cache") as mock_cache:
            mock_cache.set.return_value = None
            mock_cache.get.return_value = "wrong"
            response = health_ready(request)

        assert response.status_code == 503
        data = json.loads(response.content)
        assert "Cache: unavailable" in data["errors"]
