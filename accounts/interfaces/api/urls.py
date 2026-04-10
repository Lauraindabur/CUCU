from django.urls import path

from .views import (
    LoginAPIView,
    MeAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    RegisterAPIView,
    TokenRefreshAPIView,
)

urlpatterns = [
    path("registro", RegisterAPIView.as_view(), name="registro"),
    path("registro/", RegisterAPIView.as_view(), name="registro-slash"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("login/", LoginAPIView.as_view(), name="login-slash"),
    path("token/refresh", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh-slash"),
    path("password-reset", PasswordResetRequestAPIView.as_view(), name="password-reset"),
    path("password-reset/", PasswordResetRequestAPIView.as_view(), name="password-reset-slash"),
    path("password-reset/confirm", PasswordResetConfirmAPIView.as_view(), name="password-reset-confirm"),
    path("password-reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="password-reset-confirm-slash"),
    path("me", MeAPIView.as_view(), name="me"),
    path("me/", MeAPIView.as_view(), name="me-slash"),
]