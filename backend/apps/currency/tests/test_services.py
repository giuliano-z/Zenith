"""Unit tests de la capa de dominio (domain/services.py) del módulo CURRENCY.

Prueban la lógica de negocio directamente, sin stack HTTP (RNF-006). El provider
se pasa como un doble que cumple la interfaz, sin patches globales. Las funciones
que tocan DB se marcan con django_db.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.currency.domain import services
from apps.currency.domain.interfaces import (
    ExchangeRateProviderError,
    ExchangeRateProviderInterface,
)
from apps.currency.models import ExchangeRate, RateType, Source

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
    )


def _make_rate(user, *, rate, effective_date, rate_type=RateType.BLUE):
    return ExchangeRate.objects.create(
        rate=Decimal(rate),
        rate_type=rate_type,
        effective_date=effective_date,
        source=Source.MANUAL,
        created_by=user,
    )


# --------------------------------------------------------------------------- #
# Dobles de prueba del provider
# --------------------------------------------------------------------------- #
class _OkProvider(ExchangeRateProviderInterface):
    def fetch_rates(self):
        return {"blue": Decimal("1380.0000"), "oficial": Decimal("1050.0000")}


class _FailingProvider(ExchangeRateProviderInterface):
    def fetch_rates(self):
        raise ExchangeRateProviderError("dolarapi caído")


# --------------------------------------------------------------------------- #
# get_latest_rate
# --------------------------------------------------------------------------- #
class TestGetLatestRate:
    def test_retorna_none_sin_registros(self):
        assert services.get_latest_rate("blue") is None

    def test_retorna_el_mas_reciente_por_effective_date(self, user):
        _make_rate(user, rate="1300", effective_date=date(2026, 6, 1))
        nueva = _make_rate(user, rate="1380", effective_date=date(2026, 6, 5))
        _make_rate(user, rate="1350", effective_date=date(2026, 6, 3))

        assert services.get_latest_rate("blue") == nueva


# --------------------------------------------------------------------------- #
# get_rate_for_date (RF-018 — integración DASHBOARD)
# --------------------------------------------------------------------------- #
class TestGetRateForDate:
    def test_retorna_la_tasa_de_la_fecha_exacta(self, user):
        objetivo = _make_rate(user, rate="1360", effective_date=date(2026, 6, 4))
        _make_rate(user, rate="1380", effective_date=date(2026, 6, 6))

        assert services.get_rate_for_date(date(2026, 6, 4), "blue") == objetivo

    def test_usa_la_anterior_si_no_hay_exacta(self, user):
        anterior = _make_rate(user, rate="1340", effective_date=date(2026, 6, 1))
        _make_rate(user, rate="1400", effective_date=date(2026, 6, 10))

        # El 5/6 no tiene tasa propia: vale la del 1/6 (sigue vigente).
        assert services.get_rate_for_date(date(2026, 6, 5), "blue") == anterior


# --------------------------------------------------------------------------- #
# fetch_live_rates
# --------------------------------------------------------------------------- #
class TestFetchLiveRates:
    def test_retorna_datos_del_provider_cuando_funciona(self):
        result = services.fetch_live_rates(_OkProvider())

        assert result == {
            "blue": Decimal("1380.0000"),
            "oficial": Decimal("1050.0000"),
        }
        assert "error" not in result

    def test_retorna_fallback_cuando_provider_falla_con_db(self, user):
        ultimo = _make_rate(user, rate="1375", effective_date=date(2026, 6, 6))

        result = services.fetch_live_rates(_FailingProvider())

        assert result["error"] == "dolarapi caído"
        assert result["fallback"] == ultimo

    def test_retorna_error_cuando_provider_falla_sin_db(self):
        result = services.fetch_live_rates(_FailingProvider())

        assert result["error"] == "dolarapi caído"
        assert result["fallback"] is None
