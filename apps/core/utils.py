from ipware import get_client_ip as _get_client_ip

try:
    import inflect
    _inflect_engine = inflect.engine()
except ImportError:
    _inflect_engine = None


def get_client_ip(request) -> str:
    """
    Extract the real client IP address from the request.
    Uses django-ipware for safe IP extraction that handles
    X-Forwarded-For header spoofing protection.
    """
    ip, _ = _get_client_ip(request)
    return ip or ""


def singularize(plural: str) -> str:
    """복수형 snake_case → 단수형 snake_case"""
    if _inflect_engine is None:
        if plural.endswith("ies"):
            return plural[:-3] + "y"
        if plural.endswith(("ses", "xes", "zes")):
            return plural[:-2]
        if plural.endswith("s") and not plural.endswith("ss"):
            return plural[:-1]
        return plural
    result = _inflect_engine.singular_noun(plural)
    if result is False:
        return plural
    return result


def to_pascal(snake: str) -> str:
    """snake_case → PascalCase"""
    return "".join(word.capitalize() for word in snake.split("_"))
