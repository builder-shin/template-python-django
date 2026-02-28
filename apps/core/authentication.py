from rest_framework.authentication import BaseAuthentication
from apps.auth_service.client import AuthServiceClient, AuthenticationError, ServiceUnavailableError
from apps.core.exceptions import JsonApiError


class CookieSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("session_web")
        if not token:
            return None
        try:
            client = AuthServiceClient()
            user = client.verify_session(token)
            if user is None:
                return None
            return (user, token)
        except AuthenticationError:
            return None
        except ServiceUnavailableError:
            raise JsonApiError(
                "Service Unavailable",
                "인증 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
                503,
            )
