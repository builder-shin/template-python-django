"""SoftDelete API 통합 테스트 — Phase 5 TDD Red."""

import pytest
from rest_framework.test import APIClient

from apps.posts.models import Post
from tests.factories import CommentFactory, PostFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestDestroyAction:
    """DELETE 요청 시 soft delete 동작."""

    def test_destroy_soft_deletes_when_mixin_present(self, mock_authenticated, jsonapi_headers):
        post = PostFactory(user=mock_authenticated)
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.delete(f"/api/v1/posts/{post.pk}", **jsonapi_headers)

        assert response.status_code == 204
        assert Post.objects.filter(pk=post.pk).exists() is False
        assert Post.all_objects.filter(pk=post.pk).exists() is True

        post.refresh_from_db()
        assert post.is_deleted is True

    def test_destroy_cascades_soft_delete_to_children(self, mock_authenticated, jsonapi_headers):
        post = PostFactory(user=mock_authenticated)
        comment = CommentFactory(post=post, user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        client.delete(f"/api/v1/posts/{post.pk}", **jsonapi_headers)

        comment.refresh_from_db()
        assert comment.is_deleted is True


class TestRestoreAction:
    """POST /restore 엔드포인트."""

    def test_restore_action_returns_200(self, mock_authenticated, jsonapi_headers):
        post = PostFactory(user=mock_authenticated)
        post.delete()

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.post(f"/api/v1/posts/{post.pk}/restore", **jsonapi_headers)

        assert response.status_code == 200

    def test_restore_action_restores_deleted_instance(self, mock_authenticated, jsonapi_headers):
        post = PostFactory(user=mock_authenticated)
        post.delete()

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        client.post(f"/api/v1/posts/{post.pk}/restore", **jsonapi_headers)

        post.refresh_from_db()
        assert post.is_deleted is False

    def test_restore_action_404_for_non_existent(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.post("/api/v1/posts/99999/restore", **jsonapi_headers)

        assert response.status_code == 404

    def test_restore_action_409_for_already_active(self, mock_authenticated, jsonapi_headers):
        post = PostFactory(user=mock_authenticated)

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.post(f"/api/v1/posts/{post.pk}/restore", **jsonapi_headers)

        assert response.status_code == 409

    def test_restore_returns_404_for_non_owner(self, mock_authenticated, jsonapi_headers):
        other_user = UserFactory()
        post = PostFactory(user=other_user)
        post.delete()

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.post(f"/api/v1/posts/{post.pk}/restore", **jsonapi_headers)

        assert response.status_code == 404

    def test_restore_returns_401_for_unauthenticated(self, jsonapi_headers):
        post = PostFactory()
        post.delete()

        client = APIClient()

        response = client.post(f"/api/v1/posts/{post.pk}/restore", **jsonapi_headers)

        assert response.status_code == 401


class TestRestoreAccessControl:
    """owner_field 없는 모델의 restore 접근 제어."""

    def test_restore_returns_403_when_no_owner_field(self, mock_authenticated, jsonapi_headers):
        """owner_field를 존재하지 않는 필드로 설정하면 403 반환."""
        from unittest.mock import patch

        post = PostFactory(user=mock_authenticated)
        post.delete()

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        # owner_field를 존재하지 않는 필드명으로 패치하여 "owner_field 없는 모델" 시뮬레이션
        with patch.object(
            type(client.handler._force_user),  # dummy; we patch the view
            "__module__",
            create=True,
        ):
            from apps.posts.views import PostsViewSet

            original = getattr(PostsViewSet, "owner_field", "user")
            PostsViewSet.owner_field = "nonexistent_field"
            try:
                response = client.post(f"/api/v1/posts/{post.pk}/restore", **jsonapi_headers)
                assert response.status_code == 403
            finally:
                if original == "user":
                    # Reset to default (not explicitly set)
                    if hasattr(PostsViewSet, "owner_field"):
                        del PostsViewSet.owner_field
                else:
                    PostsViewSet.owner_field = original


class TestGetExcludesSoftDeleted:
    """Soft-deleted 인스턴스는 일반 GET에서 제외."""

    def test_get_object_excludes_soft_deleted(self, mock_authenticated, jsonapi_headers):
        post = PostFactory(user=mock_authenticated)
        post.delete()

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.get(f"/api/v1/posts/{post.pk}", **jsonapi_headers)

        assert response.status_code == 404

    def test_list_excludes_soft_deleted(self, mock_authenticated, jsonapi_headers):
        PostFactory(user=mock_authenticated, title="alive post")
        deleted = PostFactory(user=mock_authenticated, title="deleted post")
        deleted.delete()

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)

        response = client.get("/api/v1/posts", **jsonapi_headers)

        data = response.json()
        titles = [item["attributes"]["title"] for item in data["data"]]
        assert "alive post" in titles
        assert "deleted post" not in titles
