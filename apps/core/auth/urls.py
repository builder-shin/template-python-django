from django.urls import path

from apps.core.auth.views import LoginView, LogoutAllView, LogoutView, RefreshView

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/logout-all", LogoutAllView.as_view(), name="auth-logout-all"),
]
