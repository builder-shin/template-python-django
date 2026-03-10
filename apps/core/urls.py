from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.utils import singularize

# HTTP method → action 매핑 (ViewSet.as_view() 용)
_LIST_ACTIONS = {"list": "get", "create": "post"}
_DETAIL_ACTIONS = {
    "retrieve": "get",
    "update": "put",
    "partial_update": "patch",
    "destroy": "delete",
}
# 커스텀 @action 매핑: action_name → (url_path, http_method)
_CUSTOM_ACTIONS = {
    "new": ("new", "get"),
    "upsert": ("upsert", "put"),
}


def make_urlpatterns(*registrations):
    """
    URL 보일러플레이트를 줄이는 유틸리티.

    Usage:
        urlpatterns = make_urlpatterns(
            ("posts", PostsViewSet),                              # 전체 CRUD, basename 자동 추론
            ("posts", PostsViewSet, "post"),                      # 전체 CRUD, 명시적 basename
            ("posts", PostsViewSet, None, ["list", "retrieve"]),  # action 제한, basename 자동 추론
            ("posts", PostsViewSet, "post", ["list", "retrieve"]),# action 제한, 명시적 basename
        )
    """
    router = DefaultRouter(trailing_slash=False)
    only_patterns = []

    for reg in registrations:
        prefix, viewset = reg[0], reg[1]
        basename = reg[2] if len(reg) > 2 and reg[2] is not None else singularize(prefix)
        only = reg[3] if len(reg) > 3 else None

        if only is None:
            router.register(prefix, viewset, basename=basename)
        else:
            only_patterns.extend(_make_restricted_patterns(prefix, viewset, basename, only))

    result = []
    if router.registry:
        result.append(path("", include(router.urls)))
    result.extend(only_patterns)
    return result


def _make_restricted_patterns(prefix, viewset, basename, only):
    """only에 지정된 action만 포함하는 URL 패턴을 수동 생성."""
    only_set = set(only)
    patterns = []

    list_mapping = {_LIST_ACTIONS[a]: a for a in only_set if a in _LIST_ACTIONS}
    detail_mapping = {_DETAIL_ACTIONS[a]: a for a in only_set if a in _DETAIL_ACTIONS}

    if list_mapping:
        patterns.append(path(prefix, viewset.as_view(list_mapping), name=f"{basename}-list"))
    if detail_mapping:
        patterns.append(path(f"{prefix}/<pk>", viewset.as_view(detail_mapping), name=f"{basename}-detail"))

    for action in only_set:
        if action in _CUSTOM_ACTIONS:
            url_suffix, method = _CUSTOM_ACTIONS[action]
            patterns.append(
                path(
                    f"{prefix}/{url_suffix}",
                    viewset.as_view({method: action}),
                    name=f"{basename}-{action}",
                )
            )

    return patterns
