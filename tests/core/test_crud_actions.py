import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient

from apps.core.exceptions import JsonApiError, NotFound
from apps.core.filters import AllowedIncludesFilter


class TestJsonApiError:
    def test_default_status(self):
        error = JsonApiError("Test", "Test detail")
        assert error.status_code == 500
        assert error.title == "Test"
        assert error.detail == "Test detail"

    def test_custom_status(self):
        error = JsonApiError("Bad", "Bad request", 400)
        assert error.status_code == 400


class TestNotFound:
    def test_defaults(self):
        error = NotFound()
        assert error.status_code == 404
        assert error.title == "Not Found"

    def test_custom_message(self):
        error = NotFound(detail="커스텀 에러")
        assert error.detail == "커스텀 에러"


@pytest.mark.django_db
class TestCrudActionsAPI:
    def test_list_returns_jsonapi_format(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_list_unauthenticated(self, mock_unauthenticated, jsonapi_headers):
        client = APIClient()
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 401

    def test_create_returns_201(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "title": "Test Post",
                    "content": "Test content here",
                    "status": 0,
                },
            }
        }
        response = client.post(
            "/api/v1/posts",
            data=payload,
            format="vnd.api+json",
            **jsonapi_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["type"] == "posts"
        assert data["data"]["attributes"]["title"] == "Test Post"

    def test_show_returns_200(self, mock_authenticated, jsonapi_headers):
        from apps.posts.models import Post

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        post = Post.objects.create(
            title="Show Test",
            content="Content",
            user_id=str(mock_authenticated.id),
        )
        response = client.get(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 200

    def test_show_404(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts/99999", **jsonapi_headers)
        assert response.status_code == 404
        data = response.json()
        assert "errors" in data

    def test_update_returns_200(self, mock_authenticated, jsonapi_headers):
        from apps.posts.models import Post

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        post = Post.objects.create(
            title="Update Test",
            content="Content",
            user_id=str(mock_authenticated.id),
        )
        payload = {
            "data": {
                "type": "posts",
                "id": str(post.id),
                "attributes": {
                    "title": "Updated Title",
                },
            }
        }
        response = client.patch(
            f"/api/v1/posts/{post.id}",
            data=payload,
            format="vnd.api+json",
            **jsonapi_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["attributes"]["title"] == "Updated Title"

    def test_destroy_returns_204(self, mock_authenticated, jsonapi_headers):
        from apps.posts.models import Post

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        post = Post.objects.create(
            title="Delete Test",
            content="Content",
            user_id=str(mock_authenticated.id),
        )
        response = client.delete(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 204

    def test_new_action(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/posts/new", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_forbidden_update_other_user(self, mock_authenticated, jsonapi_headers):
        from apps.posts.models import Post

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        post = Post.objects.create(
            title="Other User",
            content="Content",
            user_id="different-user-id",
        )
        payload = {
            "data": {
                "type": "posts",
                "id": str(post.id),
                "attributes": {"title": "Hacked"},
            }
        }
        response = client.patch(
            f"/api/v1/posts/{post.id}",
            data=payload,
            format="vnd.api+json",
            **jsonapi_headers,
        )
        assert response.status_code == 403

    def test_forbidden_delete_other_user(self, mock_authenticated, jsonapi_headers):
        from apps.posts.models import Post

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        post = Post.objects.create(
            title="Other User Delete",
            content="Content",
            user_id="different-user-id",
        )
        response = client.delete(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 403


class TestAllowedIncludesFilter:
    def test_rejects_disallowed_includes(self):
        factory = RequestFactory()
        request = factory.get("/?include=forbidden_relation")

        class MockView:
            allowed_includes = ["category", "tags"]

        f = AllowedIncludesFilter()
        with pytest.raises(JsonApiError) as exc_info:
            f.filter_queryset(request, None, MockView())
        assert exc_info.value.status_code == 400

    def test_allows_valid_includes(self):
        factory = RequestFactory()
        request = factory.get("/?include=category")

        class MockView:
            allowed_includes = ["category", "tags"]

        f = AllowedIncludesFilter()
        result = f.filter_queryset(request, "queryset", MockView())
        assert result == "queryset"

    def test_no_include_param(self):
        factory = RequestFactory()
        request = factory.get("/")

        class MockView:
            allowed_includes = ["category"]

        f = AllowedIncludesFilter()
        result = f.filter_queryset(request, "queryset", MockView())
        assert result == "queryset"
