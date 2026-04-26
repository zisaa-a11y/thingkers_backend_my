from django.urls import path

from .views import (
    ForgotPasswordRequestView,
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    RegisterView,
    ResetPasswordConfirmView,
)

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("logout", LogoutView.as_view()),
    path("me", MeView.as_view()),
    path("forgot-password", ForgotPasswordRequestView.as_view()),
    path("reset-password", ResetPasswordConfirmView.as_view()),
]
