import importlib
import json as _json
import logging

from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured, ValidationError
from django.db import connection, models, transaction
from django.db.models import ProtectedError
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework_json_api.filters import OrderingFilter, QueryParameterValidationFilter
from rest_framework_json_api.views import ModelViewSet

from apps.core.exceptions import JsonApiError, NotFound
from apps.core.filters import AllowedIncludesFilter
from apps.core.utils import singularize, to_pascal

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


class ApiViewSet(ModelViewSet):
    """
    Base ViewSet that includes authentication, standard filter backends,
    and full CRUD lifecycle hooks.
    Equivalent to Rails ApiController + CrudActions concern.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    filter_backends = [
        QueryParameterValidationFilter,
        OrderingFilter,
        DjangoFilterBackend,
        SearchFilter,
        AllowedIncludesFilter,
    ]

    @property
    def allowed_includes(self):
        """List of allowed include paths. Enforced by AllowedIncludesFilter.

        NOTE: 반환값은 정적 리스트여야 합니다. 첫 호출 시 클래스 레벨에
        캐싱되므로, 동적(런타임 의존) 값을 반환하면 안 됩니다.
        """
        return []

    # ==================== CoC 자동 추론 ====================

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

        cache_key = "_coc_serializer_class"
        if hasattr(self.__class__, cache_key):
            return getattr(self.__class__, cache_key)

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

        klass = self._maybe_inject_included_serializers(klass)
        # NOTE: TOCTOU race between hasattr/setattr is benign — concurrent
        # threads compute identical values, so the last writer wins harmlessly.
        setattr(self.__class__, cache_key, klass)
        return klass

    def _maybe_inject_included_serializers(self, serializer_class):
        """Serializer에 included_serializers가 없으면 allowed_includes에서 추론하여 주입."""
        if getattr(serializer_class, "included_serializers", None):
            return serializer_class

        cache_key = "_coc_serializer_with_includes"
        cached = getattr(self.__class__, cache_key, None)
        if cached is not None:
            return cached

        inferred = self._infer_included_serializers()
        if inferred:
            klass = type(serializer_class.__name__, (serializer_class,), {"included_serializers": inferred})
        else:
            klass = serializer_class

        # Benign race: concurrent threads compute identical values.
        setattr(self.__class__, cache_key, klass)
        return klass

    def _infer_included_serializers(self):
        """allowed_includes + 모델 introspection으로 included_serializers 추론."""
        includes = self.allowed_includes
        if not includes:
            return {}

        # 이미 resolve된 serializer class를 우선 재사용
        serializer_cls = self.__class__.__dict__.get("serializer_class") or getattr(
            self.__class__, "_coc_serializer_class", None
        )

        if serializer_cls is None:
            app_label = self._get_app_label()
            if not app_label:
                return {}
            singular = singularize(app_label)
            class_name = f"{to_pascal(singular)}Serializer"
            module_path = f"apps.{app_label}.serializers"
            try:
                module = importlib.import_module(module_path)
                serializer_cls = getattr(module, class_name)
            except (ImportError, AttributeError):
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
        """명시적 filterset_class가 없으면 컨벤션 기반 추론."""
        if "_filterset_class" in self.__class__.__dict__:
            return self.__class__.__dict__["_filterset_class"]

        cache_key = "_coc_filterset_class"
        if hasattr(self.__class__, cache_key):
            return getattr(self.__class__, cache_key)

        app_label = self._get_app_label()
        if not app_label:
            # Benign race: concurrent threads compute identical values.
            setattr(self.__class__, cache_key, None)
            return None

        singular = singularize(app_label)
        class_name = f"{to_pascal(singular)}Filter"
        module_path = f"apps.{app_label}.filters"

        try:
            module = importlib.import_module(module_path)
            klass = getattr(module, class_name)
        except (ImportError, AttributeError):
            logger.debug("%s을 %s에서 찾을 수 없습니다. 필터 없이 동작합니다.", class_name, module_path)
            klass = None

        setattr(self.__class__, cache_key, klass)
        return klass

    @filterset_class.setter
    def filterset_class(self, value):
        """명시적 filterset_class 할당 지원.

        클래스 레벨에 저장되므로 class body 선언용으로만 사용할 것.
        DRF 내부에서 None을 할당하는 경우를 방어하기 위해 None은 무시한다.
        """
        if value is not None:
            self.__class__._filterset_class = value

    def get_base_queryset(self):
        """순수 queryset (annotation 포함). 하위 클래스에서 override."""
        model = self.get_serializer_class().Meta.model
        return model.objects.all()

    def get_queryset(self):
        """DRF의 super().get_queryset()이 요구하는 self.queryset을 설정.

        ViewSet은 요청마다 새로 생성되므로 요청 간 캐시 문제는 없다.
        같은 요청 내에서 여러 번 호출되면 첫 번째 평가 결과를 재사용한다.
        """
        if not hasattr(self, "_base_qs_cached"):
            self._base_qs_cached = True
            self.queryset = self.get_base_queryset()
        return super().get_queryset()

    def get_index_scope(self):
        """list 전용 스코핑. 기본은 get_queryset() (mixin 체인 포함)."""
        return self.get_queryset()

    # ==================== CRUD Actions ====================

    def list(self, request, *args, **kwargs):
        queryset = self.get_index_scope()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.show_after_init(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.update_after_init(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.destroy_after_init(instance)

        try:
            instance.delete()
        except ProtectedError as err:
            self.destroy_after_save(instance, False)
            raise JsonApiError("DeleteFailed", "연관된 데이터가 있어 삭제할 수 없습니다.", 409) from err
        except Exception as err:
            logger.exception("Unexpected error deleting %s(pk=%s)", type(instance).__name__, instance.pk)
            self.destroy_after_save(instance, False)
            raise JsonApiError("DeleteFailed", "리소스 삭제에 실패했습니다.", 422) from err

        self.destroy_after_save(instance, True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="new")
    def new(self, request, *args, **kwargs):
        """
        Instantiate a blank model and return its serialized form.
        Equivalent to Rails CrudActions `new` action.
        """
        model_class = self.get_serializer().Meta.model
        instance = model_class()
        self.new_after_init(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _parse_raw_body(self):
        """Parse JSONAPI raw body once and cache."""
        if not hasattr(self, "_cached_raw_body"):
            try:
                self._cached_raw_body = _json.loads(self.request._request.body)
            except (ValueError, UnicodeDecodeError):
                self._cached_raw_body = {}
        return self._cached_raw_body

    @action(detail=False, methods=["put"], url_path="upsert")
    def upsert(self, request, *args, **kwargs):
        find_params = self.upsert_find_params()
        if not find_params:
            raise JsonApiError("BadRequest", "upsert_find_params를 뷰셋에서 정의해야 합니다.", 400)

        model_class = self.get_serializer().Meta.model
        with transaction.atomic():
            try:
                instance = model_class.objects.select_for_update().get(**find_params)
                created = False
            except model_class.DoesNotExist:
                instance = model_class(**find_params)
                created = True

            self.upsert_after_init(instance)

            # Parse raw body to extract attributes, bypassing JSONAPI parser's id requirement
            raw_body = self._parse_raw_body()
            flat_data = raw_body.get("data", {}).get("attributes", {})

            serializer = self.get_serializer(instance, data=flat_data, partial=True)
            serializer.is_valid(raise_exception=True)

            for attr, value in serializer.validated_data.items():
                setattr(instance, attr, value)

            self.upsert_after_assign(instance)

            m2m_field_names = {f.name for f in instance.__class__._meta.many_to_many}
            try:
                instance.full_clean()
                instance.save()
                for attr, value in serializer.validated_data.items():
                    if attr in m2m_field_names:
                        getattr(instance, attr).set(value)
                success = True
            except ValidationError as e:
                self.upsert_after_save(instance, False, created)
                raise JsonApiError(
                    "ValidationFailed",
                    "; ".join(
                        f"{field}: {', '.join(messages)}" if field != "__all__" else ", ".join(messages)
                        for field, messages in e.message_dict.items()
                    ),
                    422,
                ) from e
            except Exception as err:
                logger.exception("Unexpected error in upsert save for %s(pk=%s)", type(instance).__name__, instance.pk)
                self.upsert_after_save(instance, False, created)
                raise JsonApiError("SaveFailed", "리소스 저장에 실패했습니다.", 422) from err

        self.upsert_after_save(instance, success, created)

        output_serializer = self.get_serializer(instance)
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output_serializer.data, status=http_status)

    # ==================== Lifecycle Hooks ====================
    # Note: create/update hooks are called by HookableSerializerMixin,
    # not directly by ApiViewSet CRUD methods.
    # destroy/show/new/upsert hooks are called directly by ApiViewSet.

    def create_after_init(self, instance: models.Model) -> None:
        pass

    def create_after_save(self, instance: models.Model, success: bool) -> None:
        pass

    def update_after_init(self, instance: models.Model) -> None:
        pass

    def update_after_assign(self, instance: models.Model) -> None:
        pass

    def update_after_save(self, instance: models.Model, success: bool) -> None:
        pass

    def destroy_after_init(self, instance: models.Model) -> None:
        pass

    def destroy_after_save(self, instance: models.Model, success: bool) -> None:
        pass

    def show_after_init(self, instance: models.Model) -> None:
        pass

    def new_after_init(self, instance: models.Model) -> None:
        pass

    def upsert_find_params(self) -> dict | None:
        return None

    def upsert_after_init(self, instance: models.Model) -> None:
        pass

    def upsert_after_assign(self, instance: models.Model) -> None:
        pass

    def upsert_after_save(self, instance: models.Model, success: bool, created: bool) -> None:
        pass

    # ==================== Overrides ====================

    def get_object(self):
        """Override to raise JSON:API NotFound instead of DRF default."""
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj = queryset.get(**filter_kwargs)
        except queryset.model.DoesNotExist as err:
            raise NotFound() from err
        self.check_object_permissions(self.request, obj)
        return obj
