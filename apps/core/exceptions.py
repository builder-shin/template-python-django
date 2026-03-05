import logging

from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, Throttled
from rest_framework.response import Response
from rest_framework_json_api.exceptions import exception_handler as jsonapi_exception_handler

logger = logging.getLogger(__name__)


class JsonApiError(Exception):
    def __init__(self, title, detail, status_code=500):
        self.title = title
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFound(JsonApiError):
    def __init__(self, title="Not Found", detail="해당 ID의 리소스를 찾을 수 없습니다.", status_code=404):
        super().__init__(title, detail, status_code)


_EXCEPTION_MAP = {
    AuthenticationFailed: ("401", "Unauthorized", None),  # None = use exc.detail (JWT 상세 메시지 유지)
    NotAuthenticated: ("401", "Unauthorized", "로그인 후 이용해주세요."),
    PermissionDenied: ("403", "Forbidden", None),  # None = use exc.detail
    Throttled: ("429", "Too Many Requests", "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."),
}


def _make_error_response(status_str, title, detail, status_code):
    response = Response(
        [{"status": status_str, "title": title, "detail": detail}],
        status=status_code,
    )
    response.exception = True
    return response


def json_api_exception_handler(exc, context):
    """
    Unified exception handler for the entire project.

    Handles:
    1. JsonApiError (our custom exceptions) - formats per JSON:API spec
    2. NotAuthenticated (401) - formats with Korean message
    3. PermissionDenied (403) - formats with Korean message
    4. Throttled (429) - formats with Korean rate-limit message
    5. Everything else - logs backtrace and delegates to DRF-JSONAPI's built-in handler
    """
    if isinstance(exc, JsonApiError):
        return _make_error_response(str(exc.status_code), exc.title, exc.detail, exc.status_code)

    for exc_class, (status_str, title, detail) in _EXCEPTION_MAP.items():
        if isinstance(exc, exc_class):
            detail = detail or str(exc.detail)
            return _make_error_response(status_str, title, detail, int(status_str))

    logger.exception("Unhandled exception: %s", exc)

    return jsonapi_exception_handler(exc, context)
