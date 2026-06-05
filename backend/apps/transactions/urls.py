"""Rutas del módulo TRANSACTIONS. Se montan bajo /api/transactions/ en config/urls.py.

IMPORTANTE: `transfer/` e `installment/` se definen ANTES de la ruta raíz para que
queden explícitas; la raíz "" sirve list (GET) y create simple (POST).
"""
from django.urls import path

from apps.transactions.views import (
    InstallmentCreateView,
    TransactionListCreateView,
    TransferCreateView,
)

app_name = "transactions"

urlpatterns = [
    path("", TransactionListCreateView.as_view(), name="transaction-list-create"),  # RF-009/RF-011
    path("transfer/", TransferCreateView.as_view(), name="transfer-create"),  # RF-009
    path("installment/", InstallmentCreateView.as_view(), name="installment-create"),  # RF-010
]
