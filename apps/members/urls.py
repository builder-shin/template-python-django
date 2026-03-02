from apps.core.urls import make_urlpatterns

from .views import MembersViewSet

urlpatterns = make_urlpatterns(("members", MembersViewSet, "member"))
