from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import LoginView, MeView, RefreshView, UserViewSet

app_name = "accounts"

router = DefaultRouter(trailing_slash=False)
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="refresh"),
    path("auth/me", MeView.as_view(), name="me"),
] + router.urls
