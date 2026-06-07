"""Integration tests del módulo CURRENCY con APIClient.

Cubren RF-017 y RF-018 en formato Given / When / Then, atravesando el stack HTTP
completo (routing → view → service → DB). El provider de DolarAPI se sustituye
por un doble (monkeypatch de DolarApiProvider en el módulo de las views), así no
se pega a la red real.

No hay tests de aislamiento cruzado: el historial de cotizaciones es global
(cualquier usuario autenticado lo ve completo). Sí se verifica que sin token
responde 401.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def client():
    return APIClient()


def _save_rate(user, *, rate, effective_date, rate_type=RateType.BLUE):
    return ExchangeRate.objects.create(
        rate=Decimal(rate),
        rate_type=rate_type,
        effective_date=effective_date,
        source=Source.MANUAL,
        created_by=user,
    )


class _OkProvider(ExchangeRateProviderInterface):
    def fetch_rates(self):
        return {
            "blue": Decimal("1380.0000"),
            "oficial": Decimal("1050.0000"),
            "tarjeta": Decimal("1680.0000"),
        }


class _FailingProvider(ExchangeRateProviderInterface):
    def fetch_rates(self):
        raise ExchangeRateProviderError("dolarapi caído")


# --------------------------------------------------------------------------- #
# GET /api/currency/fetch/ — RF-017 (cotización en vivo)
# --------------------------------------------------------------------------- #
class TestFetch:
    def test_200_con_datos_del_provider(self, auth_client, monkeypatch):
        monkeypatch.setattr("apps.currency.views.DolarApiProvider", _OkProvider)

        response = auth_client.get(reverse("currency:currency-fetch"))

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["blue"] == {"rate": "1380.0000", "source": "dolarapi"}
        assert body["oficial"]["rate"] == "1050.0000"
        assert body["is_fallback"] is False
        assert "fetched_at" in body

    def test_is_fallback_true_cuando_provider_falla_con_db(
        self, auth_client, user, monkeypatch
    ):
        _save_rate(user, rate="1375.0000", effective_date=date(2026, 6, 6))
        monkeypatch.setattr("apps.currency.views.DolarApiProvider", _FailingProvider)

        response = auth_client.get(reverse("currency:currency-fetch"))

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["is_fallback"] is True
        assert body["blue"] == {"rate": "1375.0000", "source": "manual"}

    def test_503_cuando_provider_falla_y_db_vacia(self, auth_client, monkeypatch):
        monkeypatch.setattr("apps.currency.views.DolarApiProvider", _FailingProvider)

        response = auth_client.get(reverse("currency:currency-fetch"))

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# --------------------------------------------------------------------------- #
# POST /api/currency/rates/ — RF-017 (carga) + GET /rates/ — RF-018 (historial)
# --------------------------------------------------------------------------- #
class TestRatesListCreate:
    def test_post_201_y_aparece_en_get(self, auth_client):
        url = reverse("currency:rate-list-create")
        payload = {
            "rate_type": "blue",
            "rate": "1380.00",
            "effective_date": "2026-06-06",
        }

        post = auth_client.post(url, payload, format="json")
        assert post.status_code == status.HTTP_201_CREATED
        assert post.json()["rate"] == "1380.0000"

        listado = auth_client.get(url)
        assert listado.status_code == status.HTTP_200_OK
        data = listado.json()
        assert len(data) == 1
        assert data[0]["rate_type"] == "blue"

    def test_get_rates_requiere_token(self, client):
        response = client.get(reverse("currency:rate-list-create"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --------------------------------------------------------------------------- #
# GET /api/currency/rates/latest/ — RF-017
# --------------------------------------------------------------------------- #
class TestRateLatest:
    def test_200_con_la_mas_reciente(self, auth_client, user):
        _save_rate(user, rate="1300.0000", effective_date=date(2026, 6, 1))
        nueva = _save_rate(user, rate="1380.0000", effective_date=date(2026, 6, 6))

        response = auth_client.get(reverse("currency:rate-latest"))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == nueva.id

    def test_404_si_no_hay_registros(self, auth_client):
        response = auth_client.get(reverse("currency:rate-latest"))
        assert response.status_code == status.HTTP_404_NOT_FOUND
