from ipware import get_client_ip as _get_client_ip


def get_client_ip(request) -> str:
    """
    Extract the real client IP address from the request.
    Uses django-ipware for safe IP extraction that handles
    X-Forwarded-For header spoofing protection.
    """
    ip, _ = _get_client_ip(request)
    return ip or ""
