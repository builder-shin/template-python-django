from apps.core.urls import make_urlpatterns

from .views import PostsViewSet

urlpatterns = make_urlpatterns(("posts", PostsViewSet))
