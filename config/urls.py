from django.conf import settings
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_live(request):
    return HttpResponse("OK", status=200)


def health_ready(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path("health/live", health_live),
    path("health/ready", health_ready),
    path("api/v1/", include("apps.members.urls")),
    path("api/v1/", include("apps.posts.urls")),
    path("api/v1/", include("apps.comments.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api-docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
