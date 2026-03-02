from apps.core.urls import make_urlpatterns

from .views import CommentsViewSet

urlpatterns = make_urlpatterns(("comments", CommentsViewSet, "comment"))
