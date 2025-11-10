from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health,
    api_root,
    RegisterView,
    LoginView,
    LogoutView,
    RecipeViewSet,
)

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipe")

urlpatterns = [
    path("", api_root, name="api-root"),
    path("health/", health, name="Health"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("", include(router.urls)),
]
