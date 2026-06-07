"""Contrato del proveedor de cotizaciones (capa de dominio).

Define la interfaz que cualquier fuente de tipos de cambio debe cumplir. El
provider concreto (DolarAPI, manual, …) se inyecta en las vistas, no se
instancia dentro de los servicios: así los tests mockean sin patches globales.

Sin imports de Django: este archivo es dominio puro.
"""
from abc import ABC, abstractmethod
from decimal import Decimal


class ExchangeRateProviderError(Exception):
    """El proveedor no pudo obtener las cotizaciones (timeout, 5xx, conexión).

    Los servicios la capturan para decidir el fallback; las vistas la traducen
    a un 503 cuando además no hay datos históricos en DB.
    """


class ExchangeRateProviderInterface(ABC):
    """Fuente de cotizaciones USD/ARS en tiempo real."""

    @abstractmethod
    def fetch_rates(self) -> dict[str, Decimal]:
        """Retorna un dict con las cotizaciones disponibles.

        Keys posibles: 'blue', 'oficial', 'tarjeta', 'mayorista'.
        Lanza ExchangeRateProviderError si no puede obtener los datos.
        """
        raise NotImplementedError
