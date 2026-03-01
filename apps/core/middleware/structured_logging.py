import json
import logging
import time

from apps.core.utils import get_client_ip

logger = logging.getLogger("api")


class StructuredLoggingMiddleware:
    FILTERED_PARAMS = {"password", "token", "secret", "api_key", "credit_card", "ssn"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        params = self._get_params(request)
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000

        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": round(duration, 2),
            "remote_ip": get_client_ip(request),
            "user_id": getattr(request.user, "id", None) if hasattr(request, "user") else None,
            "request_id": request.META.get("HTTP_X_REQUEST_ID", ""),
            "params": params,
        }
        logger.info(json.dumps(log_data))
        return response

    def _get_params(self, request):
        params = {}
        for key, value in request.GET.items():
            params[key] = "[FILTERED]" if key.lower() in self.FILTERED_PARAMS else value
        if request.method in ("POST", "PUT", "PATCH") and "json" in (request.content_type or ""):
            try:
                body = json.loads(request.body) if request.body else {}
                if isinstance(body, dict):
                    params.update(self._filter_dict(body))
            except (json.JSONDecodeError, ValueError):
                pass
        return params

    def _filter_dict(self, data):
        filtered = {}
        for key, value in data.items():
            if key.lower() in self.FILTERED_PARAMS:
                filtered[key] = "[FILTERED]"
            elif isinstance(value, dict):
                filtered[key] = self._filter_dict(value)
            else:
                filtered[key] = value
        return filtered
