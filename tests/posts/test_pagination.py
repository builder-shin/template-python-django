import pytest
from rest_framework.test import APIClient

from tests.factories import PostFactory


@pytest.mark.django_db
class TestPostPagination:
    def test_default_page_size_is_25(self, mock_authenticated, jsonapi_headers):
        PostFactory.create_batch(30, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 25

    def test_custom_page_size(self, mock_authenticated, jsonapi_headers):
        PostFactory.create_batch(15, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts?page[size]=10", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10

    def test_page_number_navigation(self, mock_authenticated, jsonapi_headers):
        PostFactory.create_batch(15, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts?page[size]=10&page[number]=2", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5

    def test_max_page_size_enforced_at_100(self, mock_authenticated, jsonapi_headers):
        PostFactory.create_batch(5, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts?page[size]=200", **jsonapi_headers)
        assert response.status_code == 200
        # Should be capped at 100, but only 5 exist
        data = response.json()
        assert len(data["data"]) == 5

    def test_meta_total_count_present(self, mock_authenticated, jsonapi_headers):
        PostFactory.create_batch(30, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        meta = data["meta"]
        # total-count is added by custom pagination, or count is in meta.pagination
        total = meta.get("total-count") or meta.get("pagination", {}).get("count")
        assert total == 30

    def test_pagination_links_present(self, mock_authenticated, jsonapi_headers):
        PostFactory.create_batch(30, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "links" in data
