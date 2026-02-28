from rest_framework_json_api.views import ModelViewSet
from apps.core.permissions import IsAuthenticated


class ApiViewSet(ModelViewSet):
    """
    Base ViewSet that includes authentication.
    Equivalent to Rails ApiController.

    Inherits from rest_framework_json_api.views.ModelViewSet which includes:
    - AutoPrefetchMixin: Introspective auto-prefetch for included resources
    - PreloadIncludesMixin: Manual select_for_includes / prefetch_for_includes
    - RelatedMixin: Handles relationship endpoints
    """

    permission_classes = [IsAuthenticated]
