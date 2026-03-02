TIMESTAMP_LOOKUPS = ["exact", "gt", "gte", "lt", "lte"]


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
            # Check if include path is allowed.
            # Supports nested paths (e.g. user.consents passes if user is allowed).
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
