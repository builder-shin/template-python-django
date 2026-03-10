from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.core.urls import make_urlpatterns


class _DummyViewSet(ViewSet):
    """URL 라우팅 테스트용 최소 ViewSet."""

    def list(self, request):
        return Response()

    def create(self, request):
        return Response()

    def retrieve(self, request, pk=None):
        return Response()

    def update(self, request, pk=None):
        return Response()

    def partial_update(self, request, pk=None):
        return Response()

    def destroy(self, request, pk=None):
        return Response()

    def new(self, request):
        return Response()

    def upsert(self, request):
        return Response()


def _collect_url_names(patterns):
    """URL 패턴 리스트에서 모든 URL name을 추출 (include 중첩 포함)."""
    names = set()
    for p in patterns:
        if hasattr(p, "url_patterns"):
            names.update(_collect_url_names(p.url_patterns))
        elif hasattr(p, "name") and p.name:
            names.add(p.name)
    return names


# ==================== basename 자동 추론 ====================


class TestBasenameInference:
    def test_two_tuple_infers_basename(self):
        """2-tuple: prefix에서 singularize하여 basename 자동 추론."""
        patterns = make_urlpatterns(("posts", _DummyViewSet))
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" in names

    def test_explicit_basename_overrides(self):
        """3-tuple: 명시적 basename이 자동 추론보다 우선."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, "article"))
        names = _collect_url_names(patterns)
        assert "article-list" in names
        assert "article-detail" in names
        assert "post-list" not in names

    def test_none_basename_infers(self):
        """basename이 None이면 자동 추론."""
        patterns = make_urlpatterns(("categories", _DummyViewSet, None))
        names = _collect_url_names(patterns)
        assert "category-list" in names

    def test_backward_compat_three_tuple(self):
        """기존 3-tuple 형식 하위 호환성 유지."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, "post"))
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" in names


# ==================== only 파라미터 ====================


class TestOnlyParameter:
    def test_only_list(self):
        """only=["list"] → list URL만 생성, detail 없음."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["list"]))
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" not in names

    def test_only_list_and_retrieve(self):
        """only=["list", "retrieve"] → list + detail URL 모두 생성."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["list", "retrieve"]))
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" in names

    def test_only_create(self):
        """only=["create"] → list URL(POST 전용) 생성, detail 없음."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["create"]))
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" not in names

    def test_only_detail_actions_only(self):
        """only=["retrieve", "update", "destroy"] → detail URL만 생성."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["retrieve", "update", "destroy"]))
        names = _collect_url_names(patterns)
        assert "post-list" not in names
        assert "post-detail" in names

    def test_only_with_explicit_basename(self):
        """only + 명시적 basename 조합."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, "article", ["list"]))
        names = _collect_url_names(patterns)
        assert "article-list" in names
        assert "article-detail" not in names

    def test_only_partial_update(self):
        """only=["partial_update"] → detail URL(PATCH 전용) 생성."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["partial_update"]))
        names = _collect_url_names(patterns)
        assert "post-detail" in names
        assert "post-list" not in names

    def test_only_new(self):
        """only=["new"] → /posts/new URL 생성."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["new"]))
        names = _collect_url_names(patterns)
        assert "post-new" in names
        assert "post-list" not in names
        assert "post-detail" not in names

    def test_only_upsert(self):
        """only=["upsert"] → /posts/upsert URL 생성."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["upsert"]))
        names = _collect_url_names(patterns)
        assert "post-upsert" in names
        assert "post-list" not in names
        assert "post-detail" not in names

    def test_only_mixed_standard_and_custom(self):
        """표준 + 커스텀 액션 혼합."""
        patterns = make_urlpatterns(("posts", _DummyViewSet, None, ["list", "retrieve", "new"]))
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" in names
        assert "post-new" in names
        assert "post-upsert" not in names


# ==================== 복수 등록 ====================


class TestMultipleRegistrations:
    def test_mixed_full_and_only(self):
        """전체 CRUD + only 제한 혼합 등록."""
        patterns = make_urlpatterns(
            ("posts", _DummyViewSet),
            ("comments", _DummyViewSet, None, ["list", "create"]),
        )
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "post-detail" in names
        assert "comment-list" in names
        assert "comment-detail" not in names

    def test_multiple_two_tuples(self):
        """복수 2-tuple 등록."""
        patterns = make_urlpatterns(
            ("posts", _DummyViewSet),
            ("comments", _DummyViewSet),
        )
        names = _collect_url_names(patterns)
        assert "post-list" in names
        assert "comment-list" in names
