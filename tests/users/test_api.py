import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestUsersAPI:
    def test_index_with_auth(self, mock_authenticated, other_user, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/users", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 2

    def test_index_unauthenticated(self, mock_unauthenticated, jsonapi_headers):
        client = APIClient()
        response = client.get("/api/v1/users", **jsonapi_headers)
        assert response.status_code == 200

    def test_show_existing(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get(f"/api/v1/users/{mock_authenticated.id}", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["attributes"]["nickname"] == "Test User"

    def test_update_own(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "users",
                "id": str(mock_authenticated.id),
                "attributes": {"nickname": "New Nick"},
            }
        }
        response = client.patch(
            f"/api/v1/users/{mock_authenticated.id}", data=payload, format="vnd.api+json", **jsonapi_headers
        )
        assert response.status_code == 200
        mock_authenticated.refresh_from_db()
        assert mock_authenticated.nickname == "New Nick"

    def test_me_action(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/users/me", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["attributes"]["nickname"] == "Test User"
