from django.urls import include, path
from rest_framework.routers import DefaultRouter


def make_urlpatterns(*registrations):
    """
    URL 보일러플레이트를 줄이는 유틸리티.

    Usage:
        urlpatterns = make_urlpatterns(("posts", PostsViewSet, "post"))
    """
    router = DefaultRouter(trailing_slash=False)
    for prefix, viewset, basename in registrations:
        router.register(prefix, viewset, basename=basename)
    return [path("", include(router.urls))]
