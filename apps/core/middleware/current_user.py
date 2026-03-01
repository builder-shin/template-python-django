import threading

_thread_locals = threading.local()


class CurrentUserMiddleware:
    """
    Thread-local middleware that stores the current user for access outside request/view context.

    Timing: user is set to None before request processing. After get_response() completes
    (i.e., after DRF authentication runs), request.user is stored in thread-local.
    The thread-local is always cleaned up in the finally block to prevent stale data
    on reused threads (e.g., Gunicorn gthread workers).

    Limitation: Current.get_user() returns None during request processing (middleware/view execution)
    because the user is only captured after get_response() returns. Use request.user directly
    within views and middleware instead.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set request_id immediately — it comes from HTTP header, available before DRF auth
        _thread_locals.request_id = request.META.get("HTTP_X_REQUEST_ID", "")
        # Initialize user to None — DRF authentication hasn't run yet at this point
        _thread_locals.user = None
        try:
            response = self.get_response(request)
            # After get_response, DRF authentication has completed and request.user is correct
            _thread_locals.user = getattr(request, "user", None)
            return response
        finally:
            # Always clean up thread-locals to prevent stale values on reused threads
            # (e.g., Gunicorn gthread workers)
            _thread_locals.user = None
            _thread_locals.request_id = ""


class Current:
    @staticmethod
    def get_user():
        return getattr(_thread_locals, "user", None)

    @staticmethod
    def set_user(user):
        _thread_locals.user = user

    @staticmethod
    def get_request_id():
        return getattr(_thread_locals, "request_id", "")

    user = property(lambda self: Current.get_user())
    request_id = property(lambda self: Current.get_request_id())
