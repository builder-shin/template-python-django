from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"comments", CommentsViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
