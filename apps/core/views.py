import json as _json
import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import connection, models
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

logger = logging.getLogger(__name__)


def health_live(request):
    return HttpResponse("OK", status=200)


def health_ready(request):
    errors = []
    # DB check
    try:
        connection.ensure_connection()
    except Exception as e:
        errors.append(f"DB: {e}")
    # Cache check
    try:
        cache.set("_health_check", "ok", 10)
        if cache.get("_health_check") != "ok":
            errors.append("Cache: read-back mismatch")
    except Exception as e:
        errors.append(f"Cache: {e}")

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
        """List of allowed include paths. Enforced by AllowedIncludesFilter."""
        return []

    def get_base_queryset(self):
        """공통 queryset (annotation 포함). 하위 클래스에서 override."""
        return super().get_queryset()

    def get_queryset(self):
        return self.get_base_queryset()

    def get_index_scope(self):
        """list 전용 스코핑. 기본은 get_base_queryset()."""
        return self.get_base_queryset()

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
        if not hasattr(self, '_cached_raw_body'):
            try:
                self._cached_raw_body = _json.loads(self.request._request.body)
            except Exception:
                self._cached_raw_body = {}
        return self._cached_raw_body

    @action(detail=False, methods=["put"], url_path="upsert")
    def upsert(self, request, *args, **kwargs):
        find_params = self.upsert_find_params()
        if not find_params:
            raise JsonApiError("BadRequest", "upsert_find_params를 뷰셋에서 정의해야 합니다.", 400)

        model_class = self.get_serializer().Meta.model
        try:
            instance = model_class.objects.get(**find_params)
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
            raise JsonApiError(  # noqa: B904 (re-raised with context via `e` in message)
                "ValidationFailed",
                "; ".join(
                    f"{field}: {', '.join(messages)}" if field != "__all__" else ", ".join(messages)
                    for field, messages in e.message_dict.items()
                ),
                422,
            )
        except Exception:
            logger.exception("Unexpected error in upsert save for %s(pk=%s)", type(instance).__name__, instance.pk)
            success = False

        self.upsert_after_save(instance, success, created)

        if not success:
            raise JsonApiError("SaveFailed", "리소스 저장에 실패했습니다.", 422)

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
