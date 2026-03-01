import logging

from django.db import connection
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from rest_framework_json_api.views import ModelViewSet
from apps.core.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


def health_live(request):
    return HttpResponse("OK", status=200)


def health_ready(request):
    errors = []
    # DB check
    try:
        connection.ensure_connection()
    except Exception as e:
        errors.append(f"DB: {e}")
    # Cache check
    try:
        cache.set("_health_check", "ok", 10)
        if cache.get("_health_check") != "ok":
            errors.append("Cache: read-back mismatch")
    except Exception as e:
        errors.append(f"Cache: {e}")

    if errors:
        return JsonResponse(
            {"status": "unavailable", "errors": errors},
            status=503,
        )
    return HttpResponse("OK", status=200)


class ApiViewSet(ModelViewSet):
    """
    Base ViewSet that includes authentication.
    Equivalent to Rails ApiController.

    Inherits from rest_framework_json_api.views.ModelViewSet which includes:
    - AutoPrefetchMixin: Introspective auto-prefetch for included resources
    - PreloadIncludesMixin: Manual select_for_includes / prefetch_for_includes
    - RelatedMixin: Handles relationship endpoints
    """

    permission_classes = [IsAuthenticated]
