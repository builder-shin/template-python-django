import pytest
from rest_framework.test import APIClient

from apps.posts.models import Post
from tests.factories import CommentFactory, PostFactory


@pytest.mark.django_db
class TestCommentValidation:
    def test_create_missing_content_returns_400(self, mock_authenticated, jsonapi_headers):
        """content 없이 Comment 생성 → 400"""
        post = PostFactory(user=mock_authenticated, status=Post.Status.PUBLISHED)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "comments",
                "attributes": {},
                "relationships": {"post": {"data": {"type": "posts", "id": str(post.id)}}},
            }
        }
        response = client.post("/api/v1/comments", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 400

    def test_create_nonexistent_post_id_returns_400(self, mock_authenticated, jsonapi_headers):
        """존재하지 않는 post_id로 Comment 생성 → 400 or 409"""
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "comments",
                "attributes": {"content": "test"},
                "relationships": {"post": {"data": {"type": "posts", "id": "99999"}}},
            }
        }
        response = client.post("/api/v1/comments", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code in (400, 404, 409)

    def test_create_unauthenticated_returns_401(self, jsonapi_headers):
        """비인증 상태에서 Comment 생성 → 401"""
        client = APIClient()
        payload = {
            "data": {
                "type": "comments",
                "attributes": {"content": "test"},
                "relationships": {"post": {"data": {"type": "posts", "id": "1"}}},
            }
        }
        response = client.post("/api/v1/comments", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 401

    def test_update_other_users_comment_returns_403(self, mock_authenticated, other_user, jsonapi_headers):
        """타인의 Comment 수정 → 403"""
        post = PostFactory(user=other_user, status=Post.Status.PUBLISHED)
        comment = CommentFactory(post=post, content="Other's comment", user=other_user)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {"data": {"type": "comments", "id": str(comment.id), "attributes": {"content": "Hacked"}}}
        response = client.patch(
            f"/api/v1/comments/{comment.id}", data=payload, format="vnd.api+json", **jsonapi_headers
        )
        assert response.status_code == 403

    def test_delete_other_users_comment_returns_403(self, mock_authenticated, other_user, jsonapi_headers):
        """타인의 Comment 삭제 → 403"""
        post = PostFactory(user=other_user, status=Post.Status.PUBLISHED)
        comment = CommentFactory(post=post, content="Other's comment", user=other_user)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.delete(f"/api/v1/comments/{comment.id}", **jsonapi_headers)
        assert response.status_code == 403
