from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import LoginView, MeView, RefreshView, UserViewSet, SessionListView

app_name = "accounts"

router = DefaultRouter(trailing_slash=False)
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/sessions", SessionListView.as_view(), name="sessions"),
    path("auth/sessions/<uuid:session_id>", SessionListView.as_view(), name="session-revoke"),
] + [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="refresh"),
    path("auth/me", MeView.as_view(), name="me"),
] + router.urls
