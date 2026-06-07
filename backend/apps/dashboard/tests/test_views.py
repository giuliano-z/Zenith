"""Integration tests del módulo DASHBOARD con APIClient.

Cubren RF-019 y RF-020 atravesando el stack HTTP completo (routing → view →
services → DB). Incluyen autenticación (401 sin token) y aislamiento entre
usuarios (RNF-005): el dashboard nunca expone datos de otro usuario.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AccountType, Currency
from apps.accounts.services import create_account
from apps.currency.models import ExchangeRate, RateType, Source
from apps.transactions.models import Category
from apps.transactions.services import create_transaction

User = get_user_model()

pytestmark = pytest.mark.django_db

YEAR, MONTH = 2026, 6


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        email="ana@zenith.app", name="Ana", password="River-Bridge-77"
    )


@pytest.fixture
def auth_client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def client():
    return APIClient()


def _account(user, currency=Currency.ARS):
    return create_account(
        user=user,
        name=f"Cuenta {currency}",
        account_type=AccountType.CASH,
        currency=currency,
        initial_balance=Decimal("0"),
    )


def _expense(user, account, amount, category_id=None):
    return create_transaction(
        user=user,
        account_id=account.id,
        amount=Decimal(amount),
        transaction_type="expense",
        date=date(YEAR, MONTH, 5),
        category_id=category_id,
    )


def _rate(user):
    return ExchangeRate.objects.create(
        rate=Decimal("1380.0000"),
        rate_type=RateType.BLUE,
        effective_date=date(YEAR, MONTH, 6),
        source=Source.MANUAL,
        created_by=user,
    )


URL = reverse("dashboard:dashboard")


class TestDashboard:
    def test_200_estructura_completa(self, auth_client_a, user_a):
        account = _account(user_a)
        cat = Category.objects.create(
            name="Alimentación", category_type=Category.CategoryType.EXPENSE, is_default=True
        )
        create_transaction(
            user=user_a,
            account_id=account.id,
            amount=Decimal("80000"),
            transaction_type="income",
            date=date(YEAR, MONTH, 5),
        )
        _expense(user_a, account, "20000", category_id=cat.id)
        _rate(user_a)

        response = auth_client_a.get(f"{URL}?year={YEAR}&month={MONTH}")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert set(body) == {
            "period",
            "summary",
            "consolidated_ars",
            "balances",
            "expenses_by_category",
            "has_exchange_rate",
        }
        assert body["period"] == {"year": YEAR, "month": MONTH}
        assert body["summary"]["ARS"]["net"] == "60000.0000"
        assert body["has_exchange_rate"] is True
        assert body["expenses_by_category"][0]["category_name"] == "Alimentación"
        assert body["expenses_by_category"][0]["percentage"] == "100.00"

    def test_401_sin_token(self, client):
        response = client.get(URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_respeta_filtro_de_periodo(self, auth_client_a, user_a):
        account = _account(user_a)
        create_transaction(
            user=user_a,
            account_id=account.id,
            amount=Decimal("12345"),
            transaction_type="income",
            date=date(YEAR, 3, 10),
        )

        # Mes 6 no tiene movimientos → summary vacío.
        r6 = auth_client_a.get(f"{URL}?year={YEAR}&month=6")
        assert r6.json()["summary"] == {}

        # Mes 3 sí.
        r3 = auth_client_a.get(f"{URL}?year={YEAR}&month=3")
        assert r3.json()["summary"]["ARS"]["income"] == "12345.0000"

    def test_year_invalido_devuelve_400(self, auth_client_a):
        response = auth_client_a.get(f"{URL}?year=abc")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_month_fuera_de_rango_devuelve_400(self, auth_client_a):
        response = auth_client_a.get(f"{URL}?month=13")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_consolidated_null_sin_tc(self, auth_client_a, user_a):
        account = _account(user_a)
        _expense(user_a, account, "5000")

        body = auth_client_a.get(f"{URL}?year={YEAR}&month={MONTH}").json()

        assert body["consolidated_ars"] is None
        assert body["has_exchange_rate"] is False

    def test_no_expone_datos_de_otro_usuario(self, auth_client_a, user_a, user_b):
        account_b = _account(user_b)
        _expense(user_b, account_b, "99999")

        body = auth_client_a.get(f"{URL}?year={YEAR}&month={MONTH}").json()

        # user_a no tiene cuentas ni movimientos: nada del user_b se filtra.
        assert body["summary"] == {}
        assert body["balances"] == []
        assert body["expenses_by_category"] == []
