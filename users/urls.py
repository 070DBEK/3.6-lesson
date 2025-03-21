from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, RefreshTokenView, UserProfileViewSet


router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename="user")


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="refresh"),

    path("", include(router.urls)),
    path("users/me/", UserProfileViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name="user-me"),
]
