"""UpsertMixin edge-case tests — covers error paths and default stubs."""

from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.posts.models import Post
from tests.factories import PostFactory


@pytest.mark.django_db
class TestUpsertFindParamsNone:
    """upsert_find_params가 None/falsy를 반환하면 400 에러."""

    def test_upsert_without_external_id_returns_400(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "title": "No external_id",
                    "content": "Content",
                },
            }
        }
        response = client.put("/api/v1/posts/upsert", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 400


@pytest.mark.django_db
class TestUpsertInvalidJsonBody:
    """_parse_raw_body에서 잘못된 JSON body 처리."""

    def test_upsert_with_malformed_json_returns_400(self, mock_authenticated):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.put(
            "/api/v1/posts/upsert",
            data=b"not valid json {{{",
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestUpsertValidationError:
    """upsert save 시 ValidationError 발생 케이스."""

    def test_upsert_validation_error_returns_422(self, mock_authenticated, jsonapi_headers):
        """published 상태인데 content가 빈 경우 ValidationError 발생."""
        PostFactory(
            title="Existing Post",
            content="Old content",
            user=mock_authenticated,
            external_id="val-err-001",
            status=Post.Status.DRAFT,
        )
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "external_id": "val-err-001",
                    "status": Post.Status.PUBLISHED,
                    "content": "",
                },
            }
        }
        response = client.put("/api/v1/posts/upsert", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 422


@pytest.mark.django_db
class TestUpsertUnexpectedError:
    """upsert save 시 예상 외 Exception 발생 케이스."""

    def test_upsert_unexpected_save_error_returns_422(self, mock_authenticated, jsonapi_headers):
        PostFactory(
            title="Will Fail",
            content="Content",
            user=mock_authenticated,
            external_id="unexp-001",
        )
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "posts",
                "attributes": {
                    "external_id": "unexp-001",
                    "title": "Updated",
                },
            }
        }
        with patch.object(Post, "save", side_effect=RuntimeError("DB connection lost")):
            response = client.put("/api/v1/posts/upsert", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 422
