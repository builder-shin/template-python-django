from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"posts", PostsViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
