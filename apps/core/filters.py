import django_filters
from django.db import models


class EnumChoiceFilter(django_filters.CharFilter):
    """
    Custom filter for Django IntegerField-with-choices (enum pattern).
    Converts string labels to their integer values before querying.
    """

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._reverse_map = {}
        if choices:
            for value, label in choices:
                if isinstance(label, str):
                    self._reverse_map[label.lower()] = value
                self._reverse_map[str(value)] = value

    def filter(self, qs, value):
        if value in (None, ""):
            return qs
        converted = self._reverse_map.get(value.lower() if isinstance(value, str) else value, value)
        return super().filter(qs, converted)


class EnumChoiceInFilter(django_filters.BaseInFilter):
    """In-filter variant of EnumChoiceFilter."""

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._reverse_map = {}
        if choices:
            for value, label in choices:
                if isinstance(label, str):
                    self._reverse_map[label.lower()] = value
                self._reverse_map[str(value)] = value

    def filter(self, qs, value):
        if not value:
            return qs
        converted = [
            self._reverse_map.get(v.lower().strip() if isinstance(v, str) else v, v)
            for v in value
        ]
        return super().filter(qs, converted)


class NotNullFilter(django_filters.BooleanFilter):
    """
    Filter for _not_null predicate: _not_null=True means field IS NOT null.
    Negates the value before passing to isnull lookup.
    """

    def filter(self, qs, value):
        if value is None:
            return qs
        # _not_null=True → isnull=False, _not_null=False → isnull=True
        return super().filter(qs, not value)


def create_ransack_filterset(model_class, filter_attributes):
    """
    Dynamically create a django-filter FilterSet that mimics Ransack predicates.
    """
    filters = {}

    for attr in filter_attributes:
        try:
            field = model_class._meta.get_field(attr)
        except Exception:
            continue

        is_enum = (
            isinstance(field, (models.IntegerField, models.SmallIntegerField, models.PositiveIntegerField))
            and field.choices
        )

        if is_enum:
            choices = field.choices
            filters[f"{attr}_eq"] = EnumChoiceFilter(field_name=attr, lookup_expr="exact", choices=choices)
            filters[f"{attr}_not_eq"] = EnumChoiceFilter(
                field_name=attr, lookup_expr="exact", exclude=True, choices=choices
            )
            filters[f"{attr}_in"] = EnumChoiceInFilter(field_name=attr, lookup_expr="in", choices=choices)
            filters[f"{attr}_not_in"] = EnumChoiceInFilter(
                field_name=attr, lookup_expr="in", exclude=True, choices=choices
            )
        else:
            filters[f"{attr}_eq"] = django_filters.CharFilter(field_name=attr, lookup_expr="exact")
            filters[f"{attr}_not_eq"] = django_filters.CharFilter(field_name=attr, exclude=True, lookup_expr="exact")
            filters[f"{attr}_in"] = django_filters.BaseInFilter(field_name=attr, lookup_expr="in")
            filters[f"{attr}_not_in"] = django_filters.BaseInFilter(
                field_name=attr, lookup_expr="in", exclude=True
            )

        filters[f"{attr}_cont"] = django_filters.CharFilter(field_name=attr, lookup_expr="icontains")
        filters[f"{attr}_matches"] = django_filters.CharFilter(field_name=attr, lookup_expr="regex")
        filters[f"{attr}_lt"] = django_filters.CharFilter(field_name=attr, lookup_expr="lt")
        filters[f"{attr}_lte"] = django_filters.CharFilter(field_name=attr, lookup_expr="lte")
        filters[f"{attr}_lteq"] = django_filters.CharFilter(field_name=attr, lookup_expr="lte")  # Rails 호환
        filters[f"{attr}_gt"] = django_filters.CharFilter(field_name=attr, lookup_expr="gt")
        filters[f"{attr}_gte"] = django_filters.CharFilter(field_name=attr, lookup_expr="gte")
        filters[f"{attr}_gteq"] = django_filters.CharFilter(field_name=attr, lookup_expr="gte")  # Rails 호환

        # Additional Ransack predicates
        filters[f"{attr}_not_cont"] = django_filters.CharFilter(
            field_name=attr, lookup_expr="icontains", exclude=True
        )
        filters[f"{attr}_start"] = django_filters.CharFilter(field_name=attr, lookup_expr="istartswith")
        filters[f"{attr}_end"] = django_filters.CharFilter(field_name=attr, lookup_expr="iendswith")
        filters[f"{attr}_null"] = django_filters.BooleanFilter(field_name=attr, lookup_expr="isnull")
        filters[f"{attr}_not_null"] = NotNullFilter(field_name=attr, lookup_expr="isnull")

    meta_attrs = {
        "model": model_class,
        "fields": [],
    }
    Meta = type("Meta", (), meta_attrs)
    filterset_attrs = {"Meta": Meta}
    filterset_attrs.update(filters)

    return type(f"{model_class.__name__}RansackFilterSet", (django_filters.FilterSet,), filterset_attrs)


class AllowedIncludesFilter:
    """
    Filter backend that enforces allowed include paths.
    """

    def filter_queryset(self, request, queryset, view):
        query_params = getattr(request, "query_params", request.GET)
        include_param = query_params.get("include", "")
        if not include_param:
            return queryset

        allowed = getattr(view, "allowed_includes", [])
        if not allowed:
            return queryset

        requested = [inc.strip() for inc in include_param.split(",") if inc.strip()]
        def _is_include_allowed(inc, allowed_list):
            """Check if include path is allowed. Supports nested paths (e.g. user.consents passes if user is allowed)."""
            if inc in allowed_list:
                return True
            # Nested path: check if top-level is allowed
            top_level = inc.split(".")[0]
            return top_level in allowed_list

        disallowed = [inc for inc in requested if not _is_include_allowed(inc, allowed)]
        if disallowed:
            from apps.core.exceptions import JsonApiError

            raise JsonApiError(
                "InvalidInclude",
                f"허용되지 않는 include 경로입니다: {', '.join(disallowed)}",
                400,
            )

        return queryset
