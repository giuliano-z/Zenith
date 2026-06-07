"""Rutas del módulo SHARED. Se montan bajo /api/shared/ en config/urls.py.

IMPORTANTE: `balance/settle/` se define ANTES de `balance/` para que la ruta más
corta no capture la sub-ruta de saldar.
"""
from django.urls import path

from apps.shared.views import (
    SharedBalanceView,
    SharedExpenseListCreateView,
    SharedSettleView,
)

app_name = "shared"

urlpatterns = [
    path("balance/settle/", SharedSettleView.as_view(), name="balance-settle"),  # RF-024
    path("balance/", SharedBalanceView.as_view(), name="balance"),  # RF-023
    path("expenses/", SharedExpenseListCreateView.as_view(), name="expense-list-create"),  # RF-022
]
