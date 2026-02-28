import logging
import traceback

from rest_framework.exceptions import NotAuthenticated, PermissionDenied, Throttled
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
        response = Response(
            [{
                "status": str(exc.status_code),
                "title": exc.title,
                "detail": exc.detail,
            }],
            status=exc.status_code,
        )
        response.exception = True
        return response

    if isinstance(exc, NotAuthenticated):
        response = Response(
            [{
                "status": "401",
                "title": "Unauthorized",
                "detail": str(exc.detail),
            }],
            status=401,
        )
        response.exception = True
        return response

    if isinstance(exc, PermissionDenied):
        response = Response(
            [{
                "status": "403",
                "title": "Forbidden",
                "detail": str(exc.detail),
            }],
            status=403,
        )
        response.exception = True
        return response

    if isinstance(exc, Throttled):
        response = Response(
            [{
                "status": "429",
                "title": "Too Many Requests",
                "detail": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
            }],
            status=429,
        )
        response.exception = True
        return response

    # Log backtrace for unhandled exceptions before delegating
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())

    return jsonapi_exception_handler(exc, context)
