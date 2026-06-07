"""Rutas del módulo CURRENCY. Se montan bajo /api/currency/ en config/urls.py.

IMPORTANTE: `rates/latest/` se define ANTES de cualquier ruta con <pk>. Si en el
futuro se agrega `rates/<int:pk>/`, Django intentaría resolver "latest" como un
entero y devolvería un 404 silencioso en lugar de ejecutar la vista de latest.
"""
from django.urls import path

from apps.currency.views import (
    CurrencyFetchView,
    ExchangeRateLatestView,
    ExchangeRateListCreateView,
)

app_name = "currency"

urlpatterns = [
    path("fetch/", CurrencyFetchView.as_view(), name="currency-fetch"),  # RF-017 (live)
    path(
        "rates/latest/", ExchangeRateLatestView.as_view(), name="rate-latest"
    ),  # RF-017 (antes de un eventual <pk>)
    path(
        "rates/", ExchangeRateListCreateView.as_view(), name="rate-list-create"
    ),  # RF-018 (GET) / RF-017 (POST)
]
