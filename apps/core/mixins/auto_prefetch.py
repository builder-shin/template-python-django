"""Auto select_related/prefetch_related mixin for N+1 query prevention."""

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from rest_framework_json_api.relations import ResourceRelatedField


class AutoPrefetchMixin:
    """Build optimized querysets via CoC: auto select_related/prefetch_related.

    1. Serializer의 ResourceRelatedField 중 FK/OneToOne인 것은 자동 select_related.
    2. allowed_includes의 FK는 select_related, 역참조/M2M은 prefetch_related.
    """

    ordering = ["-created_at"]
    select_related_extra: list[str] = []
    prefetch_related_extra: list[str] = []

    @staticmethod
    def _is_forward_fk(model, name):
        """Return True if *name* is a FK or OneToOne field on *model*."""
        try:
            field = model._meta.get_field(name)
        except FieldDoesNotExist:
            return False
        return field.many_to_one or field.one_to_one

    @staticmethod
    def _add_prefetch(model, name, prefetch: list) -> None:
        """Add a reverse FK / M2M relation to the prefetch list with nested select_related."""
        try:
            field = model._meta.get_field(name)
        except FieldDoesNotExist:
            return
        if field.one_to_many or field.many_to_many:
            related_model = field.related_model
            related_fks = [
                f.name
                for f in related_model._meta.get_fields()
                if hasattr(f, "related_model") and (f.many_to_one or f.one_to_one)
            ]
            if related_fks:
                prefetch.append(models.Prefetch(name, queryset=related_model.objects.select_related(*related_fks)))
            else:
                prefetch.append(name)

    def _collect_serializer_fk_fields(self, serializer_class, model, select: list) -> None:
        """Auto-detect FK/OneToOne fields from serializer's ResourceRelatedField declarations."""
        for field_name, field in serializer_class._declared_fields.items():
            if not isinstance(field, ResourceRelatedField):
                continue
            if self._is_forward_fk(model, field_name) and field_name not in select:
                select.append(field_name)

    def _collect_include_fields(self, model, select: list, prefetch: list) -> None:
        """Collect select_related/prefetch_related from allowed_includes."""
        for name in self.allowed_includes:
            if name in select:
                continue
            if self._is_forward_fk(model, name):
                select.append(name)
            else:
                self._add_prefetch(model, name, prefetch)

    def get_queryset(self):
        """Build optimized queryset via CoC: auto select_related/prefetch_related."""
        serializer_class = self.get_serializer_class()
        model = serializer_class.Meta.model
        qs = model.objects.all()

        select = list(self.select_related_extra)
        prefetch = list(self.prefetch_related_extra)

        self._collect_serializer_fk_fields(serializer_class, model, select)
        self._collect_include_fields(model, select, prefetch)

        if select:
            qs = qs.select_related(*select)
        if prefetch:
            qs = qs.prefetch_related(*prefetch)

        if self.ordering:
            valid_fields = {f.name for f in model._meta.get_fields()}
            safe_ordering = [f for f in self.ordering if f.lstrip("-") in valid_fields]
            if safe_ordering:
                qs = qs.order_by(*safe_ordering)
        return qs

    def get_index_scope(self):
        """list 전용 스코핑. 기본은 get_queryset() (mixin 체인 포함)."""
        return self.get_queryset()
