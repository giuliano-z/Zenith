"""Adapter de DolarAPI (https://dolarapi.com) — capa de infraestructura.

Implementa ExchangeRateProviderInterface contra la API pública de DolarAPI.
Fetchea blue + oficial + tarjeta (las cotizaciones más usadas por el consumidor
final). Usa el valor "venta" como rate, que es el precio al que el usuario
compra dólares.

Cualquier fallo de red (timeout, conexión rechazada, 5xx, payload inesperado)
se traduce a ExchangeRateProviderError: la capa de dominio no conoce requests.
"""
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings

from apps.currency.domain.interfaces import (
    ExchangeRateProviderError,
    ExchangeRateProviderInterface,
)

# Cotizaciones que pedimos a DolarAPI: clave interna → endpoint.
_ENDPOINTS = {
    "blue": "dolares/blue",
    "oficial": "dolares/oficial",
    "tarjeta": "dolares/tarjeta",
}


class DolarApiProvider(ExchangeRateProviderInterface):
    """Proveedor de cotizaciones en vivo desde DolarAPI."""

    def __init__(self):
        self._base_url = settings.DOLAR_API_BASE_URL.rstrip("/")
        self._timeout = settings.DOLAR_API_TIMEOUT

    def fetch_rates(self) -> dict[str, Decimal]:
        rates: dict[str, Decimal] = {}
        for key, path in _ENDPOINTS.items():
            rates[key] = self._fetch_one(path)
        return rates

    def _fetch_one(self, path: str) -> Decimal:
        url = f"{self._base_url}/{path}"
        try:
            # nosec B113 — el timeout viene de settings.DOLAR_API_TIMEOUT (no es None).
            response = requests.get(url, timeout=self._timeout)  # noqa: S113
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ExchangeRateProviderError(
                f"No se pudo obtener la cotización de {url}: {exc}"
            ) from exc

        try:
            # "venta" es el precio al que el consumidor final compra dólares.
            return Decimal(str(payload["venta"]))
        except (KeyError, TypeError, InvalidOperation) as exc:
            raise ExchangeRateProviderError(
                f"Respuesta inesperada de {url}: {payload!r}"
            ) from exc
