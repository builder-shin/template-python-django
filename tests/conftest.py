import pytest
import uuid
from unittest.mock import patch

import respx

from apps.auth_service.models import AuthUser
from apps.auth_service.client import AuthServiceClient, ServiceUnavailableError


@pytest.fixture(autouse=True)
def block_outbound_http():
    """
    Block all real HTTP calls in tests, equivalent to Rails WebMock.disable_net_connect!
    Any unmocked httpx request will raise an error instead of making a real network call.
    """
    with respx.mock:
        yield


@pytest.fixture
def auth_user():
    return AuthUser(
        id=str(uuid.uuid4()),
        email="test@example.com",
        name="Test User",
        workspace_id=str(uuid.uuid4()),
        workspace_kind="personal",
        workspace_role="owner",
        member_status="active",
    )


@pytest.fixture
def enterprise_user(auth_user):
    auth_user.workspace_kind = "enterprise"
    return auth_user


@pytest.fixture
def mock_authenticated(auth_user):
    with patch.object(AuthServiceClient, "verify_session", return_value=auth_user):
        yield auth_user


@pytest.fixture
def mock_enterprise(enterprise_user):
    with patch.object(AuthServiceClient, "verify_session", return_value=enterprise_user):
        yield enterprise_user


@pytest.fixture
def mock_unauthenticated():
    with patch.object(AuthServiceClient, "verify_session", return_value=None):
        yield


@pytest.fixture
def mock_auth_unavailable():
    with patch.object(
        AuthServiceClient,
        "verify_session",
        side_effect=ServiceUnavailableError("인증 서비스에 연결할 수 없습니다."),
    ):
        yield


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
