"""Rutas del módulo ACCOUNTS. Se montan bajo /api/accounts/ en config/urls.py.

IMPORTANTE: `balance/` se define ANTES de `<int:pk>/`. Si fuera al revés, Django
intentaría resolver "balance" como un entero para el detalle y devolvería un 404
silencioso en lugar de ejecutar la vista de balance consolidado.
"""
from django.urls import path

from apps.accounts.views import (
    AccountBalanceView,
    AccountDetailView,
    AccountListCreateView,
)

app_name = "accounts"

urlpatterns = [
    path("", AccountListCreateView.as_view(), name="account-list-create"),  # RF-005/RF-006
    path("balance/", AccountBalanceView.as_view(), name="account-balance"),  # CU-004 (antes de pk)
    path("<int:pk>/", AccountDetailView.as_view(), name="account-detail"),  # CU-003
]
