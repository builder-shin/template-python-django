import logging

from django.db.models import ProtectedError
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
from apps.core.mixins import (
    AutoPrefetchMixin,
    CoCSerializerMixin,
    LifecycleHookMixin,
    UpsertMixin,
)

logger = logging.getLogger(__name__)


class ApiViewSet(
    LifecycleHookMixin,
    UpsertMixin,
    AutoPrefetchMixin,
    CoCSerializerMixin,
    ModelViewSet,
):
    """Base ViewSet combining CoC inference, auto-prefetch, upsert, and lifecycle hooks.

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
        """Instantiate a blank model and return its serialized form."""
        model_class = self.get_serializer().Meta.model
        instance = model_class()
        self.new_after_init(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
