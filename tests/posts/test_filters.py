import pytest
from rest_framework.test import APIClient

from apps.posts.models import Post
from tests.factories import PostFactory


@pytest.mark.django_db
class TestPostFilters:
    def test_filter_title_exact(self, mock_authenticated, jsonapi_headers):
        PostFactory(title="Django Guide", user=mock_authenticated)
        PostFactory(title="Flask Guide", user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts?filter[title]=Django Guide", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["attributes"]["title"] == "Django Guide"

    def test_filter_title_icontains(self, mock_authenticated, jsonapi_headers):
        PostFactory(title="Django Guide", user=mock_authenticated)
        PostFactory(title="Advanced Django", user=mock_authenticated)
        PostFactory(title="Flask Guide", user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts?filter[title.icontains]=django", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    def test_filter_status_exact(self, mock_authenticated, jsonapi_headers):
        PostFactory(title="Draft Post", status=Post.Status.DRAFT, user=mock_authenticated)
        PostFactory(title="Published Post", status=Post.Status.PUBLISHED, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get(f"/api/v1/posts?filter[status]={Post.Status.PUBLISHED}", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["attributes"]["title"] == "Published Post"

    def test_filter_compound_title_and_status(self, mock_authenticated, jsonapi_headers):
        PostFactory(title="Django Draft", status=Post.Status.DRAFT, user=mock_authenticated)
        PostFactory(title="Django Published", status=Post.Status.PUBLISHED, user=mock_authenticated)
        PostFactory(title="Flask Draft", status=Post.Status.DRAFT, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get(
            f"/api/v1/posts?filter[title.icontains]=django&filter[status]={Post.Status.DRAFT}",
            **jsonapi_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["attributes"]["title"] == "Django Draft"

    def test_filter_no_results_returns_empty_list(self, mock_authenticated, jsonapi_headers):
        PostFactory(title="Existing Post", user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts?filter[title]=Nonexistent", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0
