from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import (
    UserRegistrationView,
    UserProfileView,
    UserPublicProfileView,
    EmailVerificationView,
    PasswordResetView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("refresh-token/", TokenRefreshView.as_view(), name="refresh-token"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    # User profile endpoints
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("<int:id>/", UserPublicProfileView.as_view(), name="user-detail"),
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
]

