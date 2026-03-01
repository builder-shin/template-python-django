from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MembersViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"members", MembersViewSet, basename="member")

urlpatterns = [
    path("", include(router.urls)),
]
