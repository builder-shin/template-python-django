import pytest
from rest_framework.test import APIClient

from apps.posts.models import Post


@pytest.mark.django_db
class TestPostsAPI:
    def test_index_with_auth(self, mock_authenticated, jsonapi_headers):
        Post.objects.create(title="Test 1", content="Content 1", user_id=mock_authenticated.id)
        Post.objects.create(title="Test 2", content="Content 2", user_id=mock_authenticated.id)

        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 2

    def test_index_unauthenticated(self, mock_unauthenticated, jsonapi_headers):
        client = APIClient()
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 401

    def test_index_only_own_posts(self, mock_authenticated, jsonapi_headers):
        Post.objects.create(title="My Post", content="Mine", user_id=mock_authenticated.id)
        Post.objects.create(title="Other Post", content="Other", user_id="other-user")

        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.get("/api/v1/posts", **jsonapi_headers)
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["attributes"]["title"] == "My Post"

    def test_create_valid(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "title": "New Post",
                    "content": "New content",
                    "status": 0,
                },
            }
        }
        response = client.post("/api/v1/posts", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["attributes"]["title"] == "New Post"
        assert data["data"]["attributes"]["user_id"] == mock_authenticated.id

    def test_show_existing(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(title="Show Me", content="Content", user_id=mock_authenticated.id)
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.get(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["attributes"]["title"] == "Show Me"

    def test_show_404(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.get("/api/v1/posts/99999", **jsonapi_headers)
        assert response.status_code == 404

    def test_update_own(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(title="Old Title", content="Content", user_id=mock_authenticated.id)
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        payload = {
            "data": {
                "type": "posts",
                "id": str(post.id),
                "attributes": {"title": "New Title"},
            }
        }
        response = client.patch(f"/api/v1/posts/{post.id}", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "New Title"

    def test_update_forbidden_other_user(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(title="Other", content="Content", user_id="other-user")
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        payload = {
            "data": {
                "type": "posts",
                "id": str(post.id),
                "attributes": {"title": "Hacked"},
            }
        }
        response = client.patch(f"/api/v1/posts/{post.id}", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 403

    def test_destroy_own(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(title="Delete Me", content="Content", user_id=mock_authenticated.id)
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.delete(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 204
        assert not Post.objects.filter(id=post.id).exists()

    def test_destroy_forbidden_other_user(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(title="Other Delete", content="Content", user_id="other-user")
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.delete(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 403

    def test_new_action(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.get("/api/v1/posts/new", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_publish_action(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(
            title="Publish Me",
            content="Good content here",
            user_id=mock_authenticated.id,
            status=0,
        )
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.post(f"/api/v1/posts/{post.id}/publish", **jsonapi_headers)
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.status == 1

    def test_publish_forbidden_other_user(self, mock_authenticated, jsonapi_headers):
        post = Post.objects.create(title="Other Pub", content="Content", user_id="other-user", status=0)
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.post(f"/api/v1/posts/{post.id}/publish", **jsonapi_headers)
        assert response.status_code == 403

    def test_publish_unauthenticated(self, mock_unauthenticated, jsonapi_headers):
        post = Post.objects.create(title="Unauth Pub", content="Content", user_id="some-user", status=0)
        client = APIClient()
        response = client.post(f"/api/v1/posts/{post.id}/publish", **jsonapi_headers)
        assert response.status_code == 401

    def test_upsert_creates_new(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "title": "Upserted Post",
                    "content": "Upsert content",
                    "external_id": "ext-001",
                },
            }
        }
        response = client.put("/api/v1/posts/upsert", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 201
        assert Post.objects.filter(external_id="ext-001").exists()

    def test_upsert_updates_existing(self, mock_authenticated, jsonapi_headers):
        Post.objects.create(
            title="Existing", content="Old content", user_id=mock_authenticated.id, external_id="ext-002"
        )
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "title": "Updated Title",
                    "external_id": "ext-002",
                },
            }
        }
        response = client.put("/api/v1/posts/upsert", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 200
        post = Post.objects.get(external_id="ext-002")
        assert post.title == "Updated Title"

    def test_index_auth_service_unavailable(self, mock_auth_unavailable, jsonapi_headers):
        client = APIClient()
        client.cookies["session_web"] = "test-token"
        response = client.get("/api/v1/posts", **jsonapi_headers)
        assert response.status_code == 503
        data = response.json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "503"
