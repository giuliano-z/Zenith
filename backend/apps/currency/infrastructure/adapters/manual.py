"""Adapter de carga manual — capa de infraestructura.

Fallback para cuando el usuario ingresa una cotización a mano en vez de traerla
de DolarAPI. Implementa la misma interfaz que DolarApiProvider, así el dominio
no distingue el origen.
"""
from decimal import Decimal

from apps.currency.domain.interfaces import ExchangeRateProviderInterface


class ManualProvider(ExchangeRateProviderInterface):
    """Proveedor de una cotización cargada manualmente."""

    def __init__(self, rate: Decimal):
        self.rate = rate

    def fetch_rates(self) -> dict[str, Decimal]:
        return {"custom": self.rate}
