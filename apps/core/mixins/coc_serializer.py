"""Convention-over-Configuration mixin for automatic serializer and filterset inference."""

import importlib
import logging

import django_filters
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured

from apps.core.utils import singularize, to_pascal

logger = logging.getLogger(__name__)


class CoCSerializerMixin:
    """Auto-infer serializer_class and filterset_class from app conventions.

    Serializer: apps.{app_label}.serializers.{ModelName}Serializer
    FilterSet: dynamically generated from allowed_filters dict
    """

    _cache = {}  # Class-level cache for CoC-inferred classes, bounded by number of ViewSet subclasses

    @classmethod
    def clear_cache(cls):
        """Clear the CoC inference cache. Call in test teardown if needed."""
        cls._cache.clear()

    @property
    def allowed_includes(self):
        """List of allowed include paths. Enforced by AllowedIncludesFilter.

        NOTE: 반환값은 정적 리스트여야 합니다. 첫 호출 시 클래스 레벨에
        캐싱되므로, 동적(런타임 의존) 값을 반환하면 안 됩니다.
        """
        return []

    @property
    def allowed_filters(self):
        """Declarative filter specification. Keys are field names, values are
        either a list of lookup expressions (e.g. ``["exact", "icontains"]``)
        or a ``django_filters.Filter`` instance for custom filters.

        NOTE: 반환값은 정적 dict여야 합니다. 첫 호출 시 클래스 레벨에
        캐싱되므로, 동적(런타임 의존) 값을 반환하면 안 됩니다.
        """
        return {}

    def _get_or_create_cached(self, cache_key, factory):
        """Look up cache_key in class-level _cache; if missing, call factory() and store.

        Uses a compound key (cls, cache_key) so different subclasses get
        independent cache entries. Dict assignment is GIL-atomic in CPython,
        so concurrent threads computing identical values is harmless.
        """
        cls = self.__class__
        compound_key = (cls, cache_key)
        if compound_key not in CoCSerializerMixin._cache:
            CoCSerializerMixin._cache[compound_key] = factory()
        return CoCSerializerMixin._cache[compound_key]

    @classmethod
    def _get_app_label(cls):
        """ViewSet 모듈 경로에서 앱 이름 추출."""
        module = cls.__module__
        parts = module.split(".")
        if len(parts) >= 3 and parts[0] == "apps" and parts[1] != "core":
            return parts[1]
        return None

    def get_serializer_class(self):
        """명시적 serializer_class가 없으면 컨벤션 기반 추론."""
        if "serializer_class" in self.__class__.__dict__:
            klass = self.__class__.__dict__["serializer_class"]
            return self._maybe_inject_included_serializers(klass)

        def _resolve():
            app_label = self._get_app_label()
            if not app_label:
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__}에 serializer_class가 지정되지 않았고, "
                    f"앱 경로에서 추론할 수 없습니다. serializer_class를 명시하세요."
                )

            singular = singularize(app_label)
            class_name = f"{to_pascal(singular)}Serializer"
            module_path = f"apps.{app_label}.serializers"

            try:
                module = importlib.import_module(module_path)
                klass = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                raise ImproperlyConfigured(
                    f"{class_name}을 {module_path}에서 찾을 수 없습니다. serializer_class를 명시하세요."
                ) from e

            return self._maybe_inject_included_serializers(klass)

        return self._get_or_create_cached("_coc_serializer_class", _resolve)

    def _maybe_inject_included_serializers(self, serializer_class):
        """Serializer에 included_serializers가 없으면 allowed_includes에서 추론하여 주입."""
        if getattr(serializer_class, "included_serializers", None):
            return serializer_class

        def _resolve():
            inferred = self._infer_included_serializers(serializer_class)
            if inferred:
                return type(
                    f"{serializer_class.__name__}WithIncludes",
                    (serializer_class,),
                    {"included_serializers": inferred},
                )
            return serializer_class

        return self._get_or_create_cached("_coc_serializer_with_includes", _resolve)

    def _resolve_serializer_cls(self, serializer_cls=None):
        """Resolve serializer class from explicit arg, class dict, cache, or convention."""
        if serializer_cls is not None:
            return serializer_cls

        serializer_cls = self.__class__.__dict__.get("serializer_class")
        if serializer_cls is None:
            serializer_cls = CoCSerializerMixin._cache.get((self.__class__, "_coc_serializer_class"))

        if serializer_cls is None:
            app_label = self._get_app_label()
            if not app_label:
                return None
            singular = singularize(app_label)
            class_name = f"{to_pascal(singular)}Serializer"
            module_path = f"apps.{app_label}.serializers"
            try:
                module = importlib.import_module(module_path)
                serializer_cls = getattr(module, class_name)
            except (ImportError, AttributeError):
                return None

        return serializer_cls

    def _infer_included_serializers(self, serializer_cls=None):
        """allowed_includes + 모델 introspection으로 included_serializers 추론."""
        includes = self.allowed_includes
        if not includes:
            return {}

        serializer_cls = self._resolve_serializer_cls(serializer_cls)
        if serializer_cls is None:
            return {}

        model = getattr(getattr(serializer_cls, "Meta", None), "model", None)
        if model is None:
            return {}

        result = {}
        for include_name in includes:
            try:
                field = model._meta.get_field(include_name)
            except FieldDoesNotExist:
                logger.warning(
                    "Field '%s' not found on %s",
                    include_name,
                    model.__name__,
                )
                continue

            related_model = getattr(field, "related_model", None)
            if related_model is None:
                logger.warning(
                    "Field '%s' on %s is not a relation",
                    include_name,
                    model.__name__,
                )
                continue

            rel_app = related_model._meta.app_label
            rel_name = related_model.__name__
            result[include_name] = f"apps.{rel_app}.serializers.{rel_name}Serializer"
        return result

    @property
    def filterset_class(self):
        """allowed_filters dict에서 FilterSet을 동적 생성."""
        if "_filterset_class" in self.__class__.__dict__:
            return self.__class__.__dict__["_filterset_class"]

        def _resolve():
            filters = self.allowed_filters
            if not filters:
                return None

            app_label = self._get_app_label()
            if not app_label:
                return None

            singular = singularize(app_label)
            try:
                models_module = importlib.import_module(f"apps.{app_label}.models")
                model = getattr(models_module, to_pascal(singular))
            except (ImportError, AttributeError):
                logger.debug(
                    "apps.%s.models.%s를 찾을 수 없습니다. 필터 없이 동작합니다.",
                    app_label,
                    to_pascal(singular),
                )
                return None

            attrs = {}
            meta_fields = {}
            for field_name, spec in filters.items():
                if isinstance(spec, django_filters.Filter):
                    attrs[field_name] = spec
                else:
                    meta_fields[field_name] = spec

            meta_cls = type("Meta", (), {"model": model, "fields": meta_fields})
            attrs["Meta"] = meta_cls

            cls_name = f"{to_pascal(singular)}DynamicFilterSet"
            return type(cls_name, (django_filters.FilterSet,), attrs)

        return self._get_or_create_cached("_coc_filterset_class", _resolve)

    @filterset_class.setter
    def filterset_class(self, value):
        """명시적 filterset_class 할당 지원.

        DRF 내부에서 None을 할당하는 경우를 방어하기 위해 None은 무시한다.
        """
        if value is not None:
            self.__class__._filterset_class = value
