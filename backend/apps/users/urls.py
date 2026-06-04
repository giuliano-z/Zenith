"""Rutas del módulo AUTH. Se montan bajo /api/auth/ en config/urls.py."""
from django.urls import path

from apps.users.views import LoginView, LogoutAllView, LogoutView, RegisterView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),  # RF-001
    path("login/", LoginView.as_view(), name="login"),  # RF-002
    path("logout/", LogoutView.as_view(), name="logout"),  # RF-003
    path("logoutall/", LogoutAllView.as_view(), name="logoutall"),
]
