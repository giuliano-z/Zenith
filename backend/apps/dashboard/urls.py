"""Rutas del módulo DASHBOARD. Se montan bajo /api/dashboard/ en config/urls.py."""
from django.urls import path

from apps.dashboard.views import DashboardView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),  # RF-019 / RF-020
]
