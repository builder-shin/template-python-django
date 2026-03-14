"""Health check endpoints for liveness and readiness probes."""

import logging

from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def health_live(request):
    return HttpResponse("OK", status=200)


def health_ready(request):
    errors = []
    # DB check
    try:
        connection.ensure_connection()
    except Exception as e:
        logger.error("Health check DB failure: %s", e)
        errors.append("DB: unavailable")
    # Cache check
    try:
        cache.set("_health_check", "ok", 10)
        if cache.get("_health_check") != "ok":
            errors.append("Cache: unavailable")
    except Exception as e:
        logger.error("Health check cache failure: %s", e)
        errors.append("Cache: unavailable")

    if errors:
        return JsonResponse(
            {"status": "unavailable", "errors": errors},
            status=503,
        )
    return HttpResponse("OK", status=200)
