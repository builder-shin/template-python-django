import pytest
from rest_framework.test import APIClient

from apps.comments.models import Comment
from apps.posts.models import Post


@pytest.mark.django_db
class TestCommentsAPI:
    def _create_post(self, user):
        return Post.objects.create(
            title="Test Post", content="Content", user=user, status=Post.Status.PUBLISHED
        )

    def test_index_with_auth(self, mock_authenticated, other_user, jsonapi_headers):
        post = self._create_post(mock_authenticated)
        Comment.objects.create(post=post, content="Comment 1", user=mock_authenticated)
        Comment.objects.create(post=post, content="Comment 2", user=other_user)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/comments", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 2

    def test_index_unauthenticated(self, mock_unauthenticated, jsonapi_headers):
        client = APIClient()
        response = client.get("/api/v1/comments", **jsonapi_headers)
        assert response.status_code == 200

    def test_create_valid(self, mock_authenticated, jsonapi_headers):
        post = self._create_post(mock_authenticated)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "comments",
                "attributes": {
                    "content": "Great post!",
                },
                "relationships": {"post": {"data": {"type": "posts", "id": str(post.id)}}},
            }
        }
        response = client.post("/api/v1/comments", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["attributes"]["content"] == "Great post!"

    def test_create_reply(self, mock_authenticated, other_user, jsonapi_headers):
        post = self._create_post(mock_authenticated)
        parent = Comment.objects.create(post=post, content="Parent", user=other_user)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "comments",
                "attributes": {
                    "content": "Reply!",
                },
                "relationships": {
                    "post": {"data": {"type": "posts", "id": str(post.id)}},
                    "parent": {"data": {"type": "comments", "id": str(parent.id)}},
                },
            }
        }
        response = client.post("/api/v1/comments", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["relationships"]["parent"]["data"] is not None

    def test_show_existing(self, mock_authenticated, jsonapi_headers):
        post = self._create_post(mock_authenticated)
        comment = Comment.objects.create(post=post, content="Show Me", user=mock_authenticated)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get(f"/api/v1/comments/{comment.id}", **jsonapi_headers)
        assert response.status_code == 200

    def test_update_own(self, mock_authenticated, jsonapi_headers):
        post = self._create_post(mock_authenticated)
        comment = Comment.objects.create(post=post, content="Old Content", user=mock_authenticated)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "comments",
                "id": str(comment.id),
                "attributes": {"content": "Updated Content"},
            }
        }
        response = client.patch(
            f"/api/v1/comments/{comment.id}", data=payload, format="vnd.api+json", **jsonapi_headers
        )
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.content == "Updated Content"

    def test_destroy_own(self, mock_authenticated, jsonapi_headers):
        post = self._create_post(mock_authenticated)
        comment = Comment.objects.create(post=post, content="Delete Me", user=mock_authenticated)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.delete(f"/api/v1/comments/{comment.id}", **jsonapi_headers)
        assert response.status_code == 204
        assert not Comment.objects.filter(id=comment.id).exists()
