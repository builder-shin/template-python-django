from rest_framework_json_api.pagination import JsonApiPageNumberPagination as BasePageNumberPagination


class JsonApiPageNumberPagination(BasePageNumberPagination):
    page_size = 25
    page_size_query_param = "page[size]"
    page_query_param = "page[number]"
    max_page_size = 100

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data.setdefault("meta", {})
        response.data["meta"]["total-count"] = self.page.paginator.count
        return response
