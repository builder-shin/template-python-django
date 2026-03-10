import importlib
from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured


class TestGetAppLabel:
    """_get_app_label() 테스트"""

    def test_posts_viewset_returns_posts(self):
        from apps.posts.views import PostsViewSet

        assert PostsViewSet._get_app_label() == "posts"

    def test_users_viewset_returns_users(self):
        from apps.users.views import UsersViewSet

        assert UsersViewSet._get_app_label() == "users"

    def test_comments_viewset_returns_comments(self):
        from apps.comments.views import CommentsViewSet

        assert CommentsViewSet._get_app_label() == "comments"

    def test_core_viewset_returns_none(self):
        from apps.core.views import ApiViewSet

        assert ApiViewSet._get_app_label() is None


class TestSingularizeAndToPascal:
    """유틸리티 함수 테스트"""

    def test_singularize_posts(self):
        from apps.core.utils import singularize

        assert singularize("posts") == "post"

    def test_singularize_users(self):
        from apps.core.utils import singularize

        assert singularize("users") == "user"

    def test_singularize_comments(self):
        from apps.core.utils import singularize

        assert singularize("comments") == "comment"

    def test_singularize_categories(self):
        from apps.core.utils import singularize

        assert singularize("categories") == "category"

    def test_singularize_already_singular(self):
        from apps.core.utils import singularize

        result = singularize("post")
        assert result == "post"

    def test_to_pascal(self):
        from apps.core.utils import to_pascal

        assert to_pascal("post") == "Post"
        assert to_pascal("order_item") == "OrderItem"
        assert to_pascal("user_profile") == "UserProfile"


class TestSingularizeFallback:
    """inflect 미설치 시 fallback singularize 로직 테스트."""

    def test_fallback_ies_suffix(self):
        """categories → category (ies → y)."""
        import apps.core.utils as utils_mod

        with patch.object(utils_mod, "_inflect_engine", None):
            assert utils_mod.singularize("categories") == "category"
            assert utils_mod.singularize("companies") == "company"

    def test_fallback_ses_suffix(self):
        """addresses → address (ses → s)."""
        import apps.core.utils as utils_mod

        with patch.object(utils_mod, "_inflect_engine", None):
            assert utils_mod.singularize("addresses") == "address"

    def test_fallback_xes_suffix(self):
        """boxes → box (xes → x)."""
        import apps.core.utils as utils_mod

        with patch.object(utils_mod, "_inflect_engine", None):
            assert utils_mod.singularize("boxes") == "box"

    def test_fallback_regular_s(self):
        """posts → post (s 제거)."""
        import apps.core.utils as utils_mod

        with patch.object(utils_mod, "_inflect_engine", None):
            assert utils_mod.singularize("posts") == "post"
            assert utils_mod.singularize("users") == "user"

    def test_fallback_ss_not_stripped(self):
        """class → class (ss로 끝나면 s 제거 안 함)."""
        import apps.core.utils as utils_mod

        with patch.object(utils_mod, "_inflect_engine", None):
            assert utils_mod.singularize("class") == "class"

    def test_fallback_no_plural_suffix(self):
        """이미 단수인 단어는 그대로 반환."""
        import apps.core.utils as utils_mod

        with patch.object(utils_mod, "_inflect_engine", None):
            assert utils_mod.singularize("child") == "child"


@pytest.mark.django_db
class TestSerializerClassInference:
    """serializer_class 자동 추론 테스트"""

    def test_posts_viewset_infers_post_serializer(self, mock_authenticated):
        """PostsViewSet에서 serializer_class 자동 추론."""
        from apps.posts.serializers import PostSerializer
        from apps.posts.views import PostsViewSet

        # Clean up any cached values from previous tests
        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(PostsViewSet, key):
                delattr(PostsViewSet, key)

        viewset = PostsViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        result = viewset.get_serializer_class()
        # PostsViewSet has allowed_includes=["comments"], so it may return a subclass
        assert issubclass(result, PostSerializer)

    def test_users_viewset_infers_user_serializer(self, mock_authenticated):
        """UsersViewSet에서 serializer_class 자동 추론."""
        from apps.users.serializers import UserSerializer
        from apps.users.views import UsersViewSet

        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(UsersViewSet, key):
                delattr(UsersViewSet, key)

        viewset = UsersViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        result = viewset.get_serializer_class()
        # UsersViewSet has no allowed_includes, so it should return exactly UserSerializer
        assert result is UserSerializer

    def test_caching_avoids_repeated_import(self, mock_authenticated):
        """추론 결과가 캐싱되어 두 번째 호출 시 importlib 미사용."""
        from apps.users.views import UsersViewSet

        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(UsersViewSet, key):
                delattr(UsersViewSet, key)

        viewset = UsersViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        # First call — triggers import
        viewset.get_serializer_class()

        # Second call — should use cache, not importlib
        with patch.object(importlib, "import_module", side_effect=AssertionError("Should not import")) as mock_import:
            viewset.get_serializer_class()

        mock_import.assert_not_called()


@pytest.mark.django_db
class TestInferIncludedSerializersEdgeCases:
    """_infer_included_serializers 방어 경로 테스트."""

    def test_nonexistent_field_in_allowed_includes(self, mock_authenticated):
        """allowed_includes에 존재하지 않는 필드 → 경고 후 스킵."""
        from apps.core.views import ApiViewSet

        class BadIncludeViewSet(ApiViewSet):
            @property
            def allowed_includes(self):
                return ["nonexistent_field"]

        BadIncludeViewSet.__module__ = "apps.posts.views"
        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(BadIncludeViewSet, key):
                delattr(BadIncludeViewSet, key)

        viewset = BadIncludeViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        result = viewset.get_serializer_class()
        included = getattr(result, "included_serializers", None)
        # 존재하지 않는 필드는 스킵되므로 빈 dict 또는 없음
        assert not included or "nonexistent_field" not in included

    def test_non_relation_field_in_allowed_includes(self, mock_authenticated):
        """allowed_includes에 관계가 아닌 필드(e.g. title) → 경고 후 스킵."""
        from apps.core.views import ApiViewSet

        class NonRelIncludeViewSet(ApiViewSet):
            @property
            def allowed_includes(self):
                return ["title"]

        NonRelIncludeViewSet.__module__ = "apps.posts.views"
        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(NonRelIncludeViewSet, key):
                delattr(NonRelIncludeViewSet, key)

        viewset = NonRelIncludeViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        result = viewset.get_serializer_class()
        included = getattr(result, "included_serializers", None)
        assert not included or "title" not in included

    def test_infer_without_serializer_cls_fallback(self, mock_authenticated):
        """serializer_cls=None으로 _infer_included_serializers 호출 시 CoC fallback."""
        from apps.core.views import ApiViewSet

        class FallbackViewSet(ApiViewSet):
            @property
            def allowed_includes(self):
                return ["comments"]

        FallbackViewSet.__module__ = "apps.posts.views"
        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(FallbackViewSet, key):
                delattr(FallbackViewSet, key)

        viewset = FallbackViewSet()
        result = viewset._infer_included_serializers(None)
        assert "comments" in result

    def test_infer_with_no_app_label_returns_empty(self):
        """app_label 추론 불가 시 빈 dict 반환."""
        from apps.core.views import ApiViewSet

        class CoreViewSet(ApiViewSet):
            @property
            def allowed_includes(self):
                return ["something"]

        # core 앱은 app_label 추론 불가
        viewset = CoreViewSet()
        result = viewset._infer_included_serializers(None)
        assert result == {}


@pytest.mark.django_db
class TestExplicitSerializerPriority:
    """명시적 serializer_class 선언이 추론보다 우선."""

    def test_explicit_serializer_class_wins(self, mock_authenticated):
        from apps.core.views import ApiViewSet
        from apps.posts.serializers import PostSerializer

        class ExplicitViewSet(ApiViewSet):
            serializer_class = PostSerializer

        ExplicitViewSet.__module__ = "apps.posts.views"

        viewset = ExplicitViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        assert viewset.get_serializer_class() is PostSerializer


@pytest.mark.django_db
class TestFiltersetClassInference:
    """filterset_class 동적 생성 테스트 (allowed_filters dict → FilterSet)"""

    def test_posts_viewset_generates_filterset(self):
        import django_filters

        from apps.posts.views import PostsViewSet

        if hasattr(PostsViewSet, "_coc_filterset_class"):
            delattr(PostsViewSet, "_coc_filterset_class")

        viewset = PostsViewSet()
        result = viewset.filterset_class
        assert result is not None
        assert issubclass(result, django_filters.FilterSet)
        assert "title" in result.Meta.fields
        assert "status" in result.Meta.fields
        assert "user" in result.Meta.fields
        assert "created_at" in result.Meta.fields
        assert "updated_at" in result.Meta.fields

    def test_core_viewset_returns_none(self):
        from apps.core.views import ApiViewSet

        if hasattr(ApiViewSet, "_coc_filterset_class"):
            delattr(ApiViewSet, "_coc_filterset_class")

        viewset = ApiViewSet()
        assert viewset.filterset_class is None

    def test_missing_filter_returns_none(self):
        """allowed_filters가 비어있으면 None 반환."""
        from apps.core.views import ApiViewSet

        class NoFilterViewSet(ApiViewSet):
            pass

        NoFilterViewSet.__module__ = "apps.nonexistent.views"

        if "_coc_filterset_class" in NoFilterViewSet.__dict__:
            delattr(NoFilterViewSet, "_coc_filterset_class")

        viewset = NoFilterViewSet()
        assert viewset.filterset_class is None

    def test_schema_generation_without_request(self):
        """filterset_class는 request 없이도 동작해야 함 (schema generation 경로)."""
        import django_filters

        from apps.core.views import ApiViewSet

        class SchemaTestViewSet(ApiViewSet):
            @property
            def allowed_filters(self):
                return {"title": ["exact", "icontains"]}

        SchemaTestViewSet.__module__ = "apps.posts.views"

        if "_coc_filterset_class" in SchemaTestViewSet.__dict__:
            delattr(SchemaTestViewSet, "_coc_filterset_class")

        viewset = SchemaTestViewSet()
        # No request, no kwargs — simulates schema generation context
        result = viewset.filterset_class
        assert result is not None
        assert issubclass(result, django_filters.FilterSet)
        assert "title" in result.Meta.fields

    def test_custom_filter_instance_in_allowed_filters(self):
        """dict value가 Filter 인스턴스이면 클래스 속성으로 부착."""
        import django_filters

        from apps.core.views import ApiViewSet

        custom_filter = django_filters.CharFilter(lookup_expr="icontains")

        class CustomFilterViewSet(ApiViewSet):
            @property
            def allowed_filters(self):
                return {
                    "title": ["exact"],
                    "custom_search": custom_filter,
                }

        CustomFilterViewSet.__module__ = "apps.posts.views"

        if "_coc_filterset_class" in CustomFilterViewSet.__dict__:
            delattr(CustomFilterViewSet, "_coc_filterset_class")

        viewset = CustomFilterViewSet()
        result = viewset.filterset_class
        assert result is not None
        assert "title" in result.Meta.fields
        # FilterSet metaclass moves Filter instances to declared_filters
        assert "custom_search" in result.declared_filters

    def test_explicit_filterset_class_override(self):
        """_filterset_class 명시적 선언이 allowed_filters보다 우선."""
        import django_filters

        from apps.core.views import ApiViewSet

        class MyFilter(django_filters.FilterSet):
            class Meta:
                from apps.posts.models import Post

                model = Post
                fields = {"title": ["exact"]}

        class OverrideViewSet(ApiViewSet):
            _filterset_class = MyFilter

            @property
            def allowed_filters(self):
                return {"status": ["exact"]}

        OverrideViewSet.__module__ = "apps.posts.views"

        viewset = OverrideViewSet()
        assert viewset.filterset_class is MyFilter


@pytest.mark.django_db
class TestIncludedSerializersInference:
    """included_serializers 자동 추론 테스트"""

    def test_comments_viewset_infers_post_serializer(self, mock_authenticated):
        """CommentsViewSet.allowed_includes = ["post"] → PostSerializer 경로 추론."""
        from apps.comments.views import CommentsViewSet
        from apps.posts.serializers import PostSerializer

        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(CommentsViewSet, key):
                delattr(CommentsViewSet, key)

        viewset = CommentsViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        serializer_class = viewset.get_serializer_class()
        included = getattr(serializer_class, "included_serializers", None)
        assert included is not None
        assert "post" in included
        # DRF-JSONAPI auto-resolves string paths to classes on access
        assert included["post"] is PostSerializer

    def test_posts_viewset_infers_comment_serializer(self, mock_authenticated):
        """PostsViewSet.allowed_includes = ["comments"] → CommentSerializer 경로 추론."""
        from apps.comments.serializers import CommentSerializer
        from apps.posts.views import PostsViewSet

        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(PostsViewSet, key):
                delattr(PostsViewSet, key)

        viewset = PostsViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        serializer_class = viewset.get_serializer_class()
        included = getattr(serializer_class, "included_serializers", None)
        assert included is not None
        assert "comments" in included
        # DRF-JSONAPI auto-resolves string paths to classes on access
        assert included["comments"] is CommentSerializer

    def test_no_includes_returns_original_serializer(self, mock_authenticated):
        """allowed_includes = [] → included_serializers 없음."""
        from apps.users.serializers import UserSerializer
        from apps.users.views import UsersViewSet

        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(UsersViewSet, key):
                delattr(UsersViewSet, key)

        viewset = UsersViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        result = viewset.get_serializer_class()
        assert result is UserSerializer
        assert not getattr(result, "included_serializers", None)


@pytest.mark.django_db
class TestExplicitIncludedSerializersPriority:
    """Serializer에 직접 선언된 included_serializers가 추론보다 우선."""

    def test_explicit_included_serializers_preserved(self, mock_authenticated):
        from rest_framework_json_api import serializers as ja_serializers

        from apps.core.views import ApiViewSet
        from apps.posts.models import Post
        from apps.posts.serializers import PostSerializer

        class MySerializer(ja_serializers.ModelSerializer):
            included_serializers = {"post": "apps.posts.serializers.PostSerializer"}

            class Meta:
                model = Post
                fields = ["title"]

        class MyViewSet(ApiViewSet):
            serializer_class = MySerializer

            @property
            def allowed_includes(self):
                return ["comments"]

        MyViewSet.__module__ = "apps.posts.views"

        viewset = MyViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        result = viewset.get_serializer_class()
        # 명시적 included_serializers가 있으면 추론하지 않고 원본 반환
        assert result is MySerializer
        assert "post" in result.included_serializers
        assert result.included_serializers["post"] is PostSerializer


@pytest.mark.django_db
class TestInferenceFailure:
    """추론 실패 시 적절한 에러."""

    def test_missing_serializer_raises_improperly_configured(self, mock_authenticated):
        from apps.core.views import ApiViewSet

        class BadViewSet(ApiViewSet):
            pass

        BadViewSet.__module__ = "apps.nonexistent.views"

        for key in ("_coc_serializer_class", "_coc_serializer_with_includes"):
            if hasattr(BadViewSet, key):
                delattr(BadViewSet, key)

        viewset = BadViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        with pytest.raises(ImproperlyConfigured) as exc_info:
            viewset.get_serializer_class()
        assert "NonexistentSerializer" in str(exc_info.value) or "serializer_class를 명시하세요" in str(exc_info.value)

    def test_core_viewset_raises_improperly_configured(self, mock_authenticated):
        """core 앱의 ApiViewSet은 추론 대상에서 제외."""
        from apps.core.views import ApiViewSet

        viewset = ApiViewSet()
        viewset.request = type("Request", (), {"user": mock_authenticated, "query_params": {}})()
        viewset.kwargs = {}
        viewset.format_kwarg = None

        with pytest.raises(ImproperlyConfigured):
            viewset.get_serializer_class()
