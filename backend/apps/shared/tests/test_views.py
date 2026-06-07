"""Integration tests del módulo SHARED con APIClient.

Cubren RF-022/023/024 atravesando el stack HTTP completo. SHARED es la excepción
al aislamiento: ambos usuarios ven los mismos datos. Se verifica además que sin
token responde 401.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AccountType, Currency
from apps.accounts.services import create_account
from apps.shared.models import SharedExpense
from apps.transactions.models import Transaction

User = get_user_model()

pytestmark = pytest.mark.django_db

TODAY = "2026-06-07"


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        email="novia@zenith.app", name="Novia", password="River-Bridge-77"
    )


@pytest.fixture
def account_a(user_a):
    return create_account(
        user=user_a,
        name="Caja A",
        account_type=AccountType.CASH,
        currency=Currency.ARS,
        initial_balance=Decimal("0"),
    )


@pytest.fixture
def client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def client_b(user_b):
    client = APIClient()
    client.force_authenticate(user=user_b)
    return client


@pytest.fixture
def client():
    return APIClient()


EXPENSES_URL = reverse("shared:expense-list-create")
BALANCE_URL = reverse("shared:balance")
SETTLE_URL = reverse("shared:balance-settle")


def _post_expense(client, account, *, total="10000.00", debtor="5000.00"):
    return client.post(
        EXPENSES_URL,
        {
            "account": account.id,
            "total_amount": total,
            "debtor_amount": debtor,
            "currency": "ARS",
            "date": TODAY,
            "description": "Cena",
        },
        format="json",
    )


class TestExpenses:
    def test_post_201_crea_transaction_en_cuenta_del_payer(
        self, client_a, user_a, user_b, account_a
    ):
        response = _post_expense(client_a, account_a)

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["payer"] == user_a.id
        assert body["debtor"] == user_b.id
        # La Transaction asociada existe, es expense y está en la cuenta del payer.
        tx = Transaction.objects.get(id=body["transaction"])
        assert tx.transaction_type == Transaction.TransactionType.EXPENSE
        assert tx.account_id == account_a.id
        assert tx.amount == Decimal("10000.00")

    def test_ambos_usuarios_ven_los_mismos_registros(
        self, client_a, client_b, user_b, account_a
    ):
        _post_expense(client_a, account_a)

        seen_by_a = client_a.get(EXPENSES_URL).json()
        seen_by_b = client_b.get(EXPENSES_URL).json()

        assert len(seen_by_a) == 1
        assert len(seen_by_b) == 1
        assert seen_by_a[0]["id"] == seen_by_b[0]["id"]

    def test_get_sin_token_devuelve_401(self, client):
        response = client.get(EXPENSES_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestBalance:
    def test_estructura_correcta(self, client_a, user_a, user_b, account_a):
        _post_expense(client_a, account_a)

        body = client_a.get(BALANCE_URL).json()

        assert body["is_balanced"] is False
        assert body["net_amount"] == "5000.0000"
        assert body["creditor"]["id"] == user_a.id
        assert body["debtor"]["id"] == user_b.id
        assert body["currency"] == "ARS"

    def test_is_balanced_sin_gastos(self, client_a, user_a, user_b):
        body = client_a.get(BALANCE_URL).json()
        assert body["is_balanced"] is True
        assert body["creditor"] is None and body["debtor"] is None


class TestSettle:
    def test_200_marca_todos_settled(self, client_a, user_a, user_b, account_a):
        _post_expense(client_a, account_a)

        response = client_a.post(SETTLE_URL, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert SharedExpense.objects.filter(is_settled=False).count() == 0

    def test_400_si_balanced(self, client_a, user_a, user_b):
        response = client_a.post(SETTLE_URL, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
