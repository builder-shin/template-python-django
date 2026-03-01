import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def block_outbound_http():
    """
    Block all real HTTP calls in tests, equivalent to Rails WebMock.disable_net_connect!
    Any unmocked httpx request will raise an error instead of making a real network call.
    """
    try:
        import respx
        with respx.mock:
            yield
    except ImportError:
        yield


@pytest.fixture
def auth_user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def mock_authenticated(auth_user):
    """Provides an authenticated user. Use with api_client fixture or force_authenticate."""
    return auth_user


@pytest.fixture
def mock_unauthenticated():
    """Marker fixture for unauthenticated tests - no user is provided."""
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, auth_user):
    """Pre-authenticated API client."""
    api_client.force_authenticate(user=auth_user)
    return api_client


@pytest.fixture
def jsonapi_headers():
    return {
        "HTTP_CONTENT_TYPE": "application/vnd.api+json",
        "HTTP_ACCEPT": "application/vnd.api+json",
    }


def jsonapi_payload(attributes, resource_type, id=None):
    data = {"type": resource_type, "attributes": attributes}
    if id:
        data["id"] = str(id)
    return {"data": data}
