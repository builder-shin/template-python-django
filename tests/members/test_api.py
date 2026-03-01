import pytest
from rest_framework.test import APIClient

from apps.members.models import Member


@pytest.mark.django_db
class TestMembersAPI:
    def test_index_with_auth(self, mock_authenticated, jsonapi_headers):
        Member.objects.create(user_id=str(mock_authenticated.id), nickname="Me")
        Member.objects.create(user_id="other-user", nickname="Other")

        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/members", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 2

    def test_index_unauthenticated(self, mock_unauthenticated, jsonapi_headers):
        client = APIClient()
        response = client.get("/api/v1/members", **jsonapi_headers)
        assert response.status_code == 401

    def test_create_valid(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "members",
                "attributes": {
                    "nickname": "New Member",
                    "bio": "Hello!",
                },
            }
        }
        response = client.post("/api/v1/members", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["attributes"]["nickname"] == "New Member"
        assert data["data"]["attributes"]["user_id"] == str(mock_authenticated.id)

    def test_show_existing(self, mock_authenticated, jsonapi_headers):
        member = Member.objects.create(user_id=str(mock_authenticated.id), nickname="Show Me")
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get(f"/api/v1/members/{member.id}", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["attributes"]["nickname"] == "Show Me"

    def test_update_own(self, mock_authenticated, jsonapi_headers):
        member = Member.objects.create(user_id=str(mock_authenticated.id), nickname="Old Nick")
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "members",
                "id": str(member.id),
                "attributes": {"nickname": "New Nick"},
            }
        }
        response = client.patch(f"/api/v1/members/{member.id}", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 200
        member.refresh_from_db()
        assert member.nickname == "New Nick"

    def test_update_forbidden_other_user(self, mock_authenticated, jsonapi_headers):
        member = Member.objects.create(user_id="other-user", nickname="Other")
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        payload = {
            "data": {
                "type": "members",
                "id": str(member.id),
                "attributes": {"nickname": "Hacked"},
            }
        }
        response = client.patch(f"/api/v1/members/{member.id}", data=payload, format="vnd.api+json", **jsonapi_headers)
        assert response.status_code == 403

    def test_destroy_own(self, mock_authenticated, jsonapi_headers):
        member = Member.objects.create(user_id=str(mock_authenticated.id), nickname="Delete Me")
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.delete(f"/api/v1/members/{member.id}", **jsonapi_headers)
        assert response.status_code == 204
        assert not Member.objects.filter(id=member.id).exists()

    def test_destroy_forbidden_other_user(self, mock_authenticated, jsonapi_headers):
        member = Member.objects.create(user_id="other-user", nickname="Other")
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.delete(f"/api/v1/members/{member.id}", **jsonapi_headers)
        assert response.status_code == 403

    def test_me_action(self, mock_authenticated, jsonapi_headers):
        Member.objects.create(user_id=str(mock_authenticated.id), nickname="My Profile")
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/members/me", **jsonapi_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["attributes"]["nickname"] == "My Profile"

    def test_me_action_not_found(self, mock_authenticated, jsonapi_headers):
        client = APIClient()
        client.force_authenticate(user=mock_authenticated)
        response = client.get("/api/v1/members/me", **jsonapi_headers)
        assert response.status_code == 404
