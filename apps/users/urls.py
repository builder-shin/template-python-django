from apps.core.urls import make_urlpatterns

from .views import UsersViewSet

urlpatterns = make_urlpatterns(("users", UsersViewSet, "user"))
