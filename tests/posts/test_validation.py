import pytest
from rest_framework.test import APIClient

from tests.factories import PostFactory


@pytest.mark.django_db
class TestPostValidation:
    def test_create_missing_title_returns_400(self, mock_authenticated, jsonapi_headers):
        """title 없이 Post 생성 → 400"""
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {"data": {"type": "posts", "attributes": {"content": "no title", "status": 0}}}
        response = client.post("/api/v1/posts", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 400

    def test_create_wrong_type_for_status_returns_400(self, mock_authenticated, jsonapi_headers):
        """status에 문자열 → 400"""
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "posts",
                "attributes": {"title": "Test", "content": "Content", "status": "invalid"},
            }
        }
        response = client.post("/api/v1/posts", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 400

    def test_create_unauthenticated_returns_401(self, jsonapi_headers):
        """비인증 상태에서 Post 생성 → 401"""
        client = APIClient()
        payload = {"data": {"type": "posts", "attributes": {"title": "Test", "content": "Content", "status": 0}}}
        response = client.post("/api/v1/posts", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 401

    def test_update_other_users_post_returns_403(self, mock_authenticated, other_user, jsonapi_headers):
        """타인의 Post 수정 → 403"""
        post = PostFactory(title="Other's Post", content="Content", user=other_user)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {"data": {"type": "posts", "id": str(post.id), "attributes": {"title": "Hacked"}}}
        response = client.patch(f"/api/v1/posts/{post.id}", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 403

    def test_delete_other_users_post_returns_403(self, mock_authenticated, other_user, jsonapi_headers):
        """타인의 Post 삭제 → 403"""
        post = PostFactory(title="Other's Post", content="Content", user=other_user)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.delete(f"/api/v1/posts/{post.id}", **jsonapi_headers)
        assert response.status_code == 403
