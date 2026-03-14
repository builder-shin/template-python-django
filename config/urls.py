from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.health import health_live, health_ready

urlpatterns = [
    path("health/live", health_live),
    path("health/ready", health_ready),
    # API v1 endpoints
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.posts.urls")),
    path("api/v1/", include("apps.comments.urls")),
    path("api/v1/", include("apps.core.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/schema", SpectacularAPIView.as_view(), name="schema-no-slash"),
        path("api-docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api-docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui-no-slash"),
    ]
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
