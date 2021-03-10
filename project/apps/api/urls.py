from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from project.apps.api.routers import router as api_router
from project.apps.api.views import AttemptViewSet, TreasureHuntViewSet, register_user

urlpatterns = [
    path("", include(api_router.urls)),
    path("auth/token/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", register_user),
    path("auth/", include("rest_framework.urls")),
]
