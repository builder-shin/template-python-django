import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


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
        nickname="Test User",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="otherpass123",
        nickname="Other User",
    )


@pytest.fixture
def mock_authenticated(auth_user):
    """Provides an authenticated user. Use with api_client fixture or force_authenticate."""
    return auth_user


@pytest.fixture
def mock_unauthenticated():
    """Marker fixture for unauthenticated tests - no user is provided."""


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, auth_user):
    """Pre-authenticated API client (force_authenticate).
    CRUD/비즈니스 로직 테스트용. JWT 미들웨어를 거치지 않음."""
    api_client.force_authenticate(user=auth_user)
    return api_client


@pytest.fixture
def jsonapi_headers():
    return {
        "HTTP_CONTENT_TYPE": "application/vnd.api+json",
        "HTTP_ACCEPT": "application/vnd.api+json",
    }


def jsonapi_payload(attributes, resource_type, resource_id=None):
    data = {"type": resource_type, "attributes": attributes}
    if resource_id:
        data["id"] = str(resource_id)
    return {"data": data}


@pytest.fixture
def auth_tokens(auth_user):
    """JWT token pair for auth_user."""
    from apps.core.auth.jwt_utils import generate_token_pair

    return generate_token_pair(auth_user)


@pytest.fixture
def access_token(auth_tokens):
    """Access token string."""
    return auth_tokens["access"]


@pytest.fixture
def jwt_authenticated_client(api_client, access_token):
    """JWT Bearer token 인증 client.
    인증 흐름(미들웨어, 토큰 검증) 테스트용."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return api_client
