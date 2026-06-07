"""Lógica de negocio del módulo CURRENCY (capa de dominio).

No depende de HTTP: ninguna función recibe un Request (RNF-006). Las vistas y
serializers consumen estas funciones. A diferencia de accounts/transactions,
acá NO hay aislamiento por usuario: el historial de cotizaciones es global
(cualquier usuario autenticado lee todo). `user` solo se usa como auditoría al
guardar (created_by).

El provider se recibe por parámetro (inyección desde la view), nunca se
instancia acá: eso mantiene el dominio testeable con un doble sin patches.
"""
from datetime import date as date_cls
from decimal import Decimal

from apps.currency.domain.interfaces import (
    ExchangeRateProviderError,
    ExchangeRateProviderInterface,
)
from apps.currency.models import ExchangeRate


def get_latest_rate(rate_type: str = "blue") -> ExchangeRate | None:
    """Retorna la tasa más reciente del tipo indicado, o None si no hay ninguna.

    El orden lo da Meta.ordering (-effective_date, -created_at): el .first() es
    la última cotización cargada para ese tipo.
    """
    return ExchangeRate.objects.filter(rate_type=rate_type).first()


def get_rate_for_date(date: date_cls, rate_type: str = "blue") -> ExchangeRate | None:
    """Tasa vigente para una fecha histórica (RF-018).

    Si no hay una cotización exacta para `date`, devuelve la última anterior:
    una tasa sigue vigente hasta que aparece otra más nueva. Es el punto de
    integración pre-arquitectado para DASHBOARD; su firma NO cambia (los callers
    solo pasan date y rate_type).
    """
    return (
        ExchangeRate.objects.filter(effective_date__lte=date, rate_type=rate_type)
        .order_by("-effective_date", "-created_at")
        .first()
    )


def save_rate(
    rate: Decimal,
    rate_type: str,
    effective_date: date_cls,
    source: str,
    user,
) -> ExchangeRate:
    """Guarda una nueva cotización en DB y retorna el objeto creado (RF-017).

    `user` queda como auditoría en created_by; no implica ownership. La
    validación de los enums (rate_type, source) la garantiza el serializer
    aguas arriba.
    """
    return ExchangeRate.objects.create(
        rate=rate,
        rate_type=rate_type,
        effective_date=effective_date,
        source=source,
        created_by=user,
    )


def fetch_live_rates(provider: ExchangeRateProviderInterface) -> dict:
    """Cotizaciones en tiempo real desde el provider inyectado. NO guarda en DB.

    Si el provider falla, captura ExchangeRateProviderError y devuelve
    {'error': mensaje, 'fallback': get_latest_rate()} para que el caller decida
    qué mostrar (la view arma is_fallback o un 503 según haya fallback o no).
    """
    try:
        return provider.fetch_rates()
    except ExchangeRateProviderError as exc:
        return {"error": str(exc), "fallback": get_latest_rate()}


__all__ = [
    "get_latest_rate",
    "get_rate_for_date",
    "save_rate",
    "fetch_live_rates",
]
