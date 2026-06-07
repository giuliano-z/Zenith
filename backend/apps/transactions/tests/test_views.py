"""Integration tests del módulo TRANSACTIONS con APIClient.

Cubren los criterios de aceptación de RF-009, RF-010 y RF-011 en formato
Given / When / Then. Atraviesan el stack HTTP completo (routing → view → service → DB).
Incluyen los tests de autorización cruzada exigidos por RNF-005 / RS-004.
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
from apps.transactions.models import Category, Transaction

User = get_user_model()

pytestmark = pytest.mark.django_db


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
def client():
    return APIClient()


@pytest.fixture
def auth_a(user_a):
    c = APIClient()
    c.force_authenticate(user=user_a)
    return c


@pytest.fixture
def auth_b(user_b):
    c = APIClient()
    c.force_authenticate(user=user_b)
    return c


@pytest.fixture
def account_a(user_a):
    return create_account(
        user=user_a, name="Caja A", account_type=AccountType.CASH,
        currency=Currency.ARS, initial_balance=Decimal("10000.00"),
    )


@pytest.fixture
def account_a_2(user_a):
    return create_account(
        user=user_a, name="MP A", account_type=AccountType.DIGITAL_WALLET,
        currency=Currency.ARS, initial_balance=Decimal("5000.00"),
    )


@pytest.fixture
def account_b(user_b):
    return create_account(
        user=user_b, name="Caja B", account_type=AccountType.CASH,
        currency=Currency.ARS, initial_balance=Decimal("3000.00"),
    )


@pytest.fixture
def category_expense(db):
    return Category.objects.create(
        name="Alimentación", category_type="expense", is_default=True
    )


def _balance(client, account_id):
    resp = client.get(reverse("accounts:account-detail", args=[account_id]))
    return Decimal(str(resp.data["balance"]))


# --------------------------------------------------------------------------- #
# RF-009 — Transacción simple
# --------------------------------------------------------------------------- #
class TestRF009Simple:
    def test_post_income_devuelve_201(self, auth_a, account_a):
        response = auth_a.post(
            reverse("transactions:transaction-list-create"),
            {
                "account_id": account_a.id,
                "amount": "1500.00",
                "transaction_type": "income",
                "date": "2026-06-01",
                "description": "Sueldo",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["transaction_type"] == "income"
        assert Decimal(str(response.data["amount"])) == Decimal("1500.00")

    def test_post_expense_devuelve_201_y_baja_balance(self, auth_a, account_a, category_expense):
        # Criterio RF-009: cuenta ARS $10.000, expense $2.000 → 201, balance $8.000.
        response = auth_a.post(
            reverse("transactions:transaction-list-create"),
            {
                "account_id": account_a.id,
                "category_id": category_expense.id,
                "amount": "2000.00",
                "transaction_type": "expense",
                "date": "2020-01-01",
                "description": "Almuerzo",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        # Y el balance de la cuenta pasa a 8000 (ADR-004)
        assert _balance(auth_a, account_a.id) == Decimal("8000.00")
        # Y la transacción aparece en GET /api/transactions/
        lista = auth_a.get(reverse("transactions:transaction-list-create"))
        assert lista.data["count"] == 1

    def test_post_sin_token_devuelve_401(self, client, account_a):
        response = client.post(
            reverse("transactions:transaction-list-create"),
            {
                "account_id": account_a.id,
                "amount": "100.00",
                "transaction_type": "expense",
                "date": "2026-06-01",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_cuenta_ajena_devuelve_403(self, auth_b, account_a):
        # B intenta crear una transacción sobre la cuenta de A (RS-004).
        response = auth_b.post(
            reverse("transactions:transaction-list-create"),
            {
                "account_id": account_a.id,
                "amount": "100.00",
                "transaction_type": "expense",
                "date": "2026-06-01",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.status_code != status.HTTP_404_NOT_FOUND


# --------------------------------------------------------------------------- #
# RF-009 — Transferencia
# --------------------------------------------------------------------------- #
class TestRF009Transfer:
    def test_post_transfer_devuelve_201_y_actualiza_ambas(
        self, auth_a, account_a, account_a_2
    ):
        # Criterio: origen $10.000, destino $5.000, transfer $3.000 → 7000 / 8000.
        response = auth_a.post(
            reverse("transactions:transfer-create"),
            {
                "from_account_id": account_a.id,
                "to_account_id": account_a_2.id,
                "amount": "3000.00",
                "date": "2020-01-01",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert _balance(auth_a, account_a.id) == Decimal("7000.00")
        assert _balance(auth_a, account_a_2.id) == Decimal("8000.00")
        # Ambas transacciones aparecen en sus historiales
        out = auth_a.get(
            reverse("transactions:transaction-list-create"),
            {"account_id": account_a.id},
        )
        inc = auth_a.get(
            reverse("transactions:transaction-list-create"),
            {"account_id": account_a_2.id},
        )
        assert out.data["results"][0]["transaction_type"] == "transfer_out"
        assert inc.data["results"][0]["transaction_type"] == "transfer_in"

    def test_post_transfer_from_account_ajena_devuelve_403(
        self, auth_a, account_b, account_a
    ):
        # A intenta transferir DESDE una cuenta de B → 403 (RS-004).
        response = auth_a.post(
            reverse("transactions:transfer-create"),
            {
                "from_account_id": account_b.id,
                "to_account_id": account_a.id,
                "amount": "100.00",
                "date": "2026-06-01",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_post_transfer_to_account_ajena_devuelve_403(
        self, auth_a, account_a, account_b
    ):
        # A intenta transferir HACIA una cuenta de B → 403 (RS-004).
        response = auth_a.post(
            reverse("transactions:transfer-create"),
            {
                "from_account_id": account_a.id,
                "to_account_id": account_b.id,
                "amount": "100.00",
                "date": "2026-06-01",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# --------------------------------------------------------------------------- #
# RF-010 — Compra en cuotas
# --------------------------------------------------------------------------- #
class TestRF010Installment:
    def test_post_installment_devuelve_201_y_N_transactions(self, auth_a, account_a):
        response = auth_a.post(
            reverse("transactions:installment-create"),
            {
                "account_id": account_a.id,
                "total_amount": "60000.00",
                "installment_count": 3,
                "first_installment_date": "2026-06-01",
                "description": "Notebook",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["transactions"]) == 3
        assert Decimal(str(response.data["amount_per_installment"])) == Decimal("20000.00")

    def test_post_installment_fechas_mensuales_correctas(self, auth_a, account_a):
        response = auth_a.post(
            reverse("transactions:installment-create"),
            {
                "account_id": account_a.id,
                "total_amount": "60000.00",
                "installment_count": 3,
                "first_installment_date": "2026-06-01",
            },
            format="json",
        )
        fechas = [t["date"] for t in response.data["transactions"]]
        assert fechas == ["2026-06-01", "2026-07-01", "2026-08-01"]


# --------------------------------------------------------------------------- #
# RF-011 — Listar con filtros, paginación y aislamiento
# --------------------------------------------------------------------------- #
class TestRF011List:
    def _seed(self, user, account, n, transaction_type="expense", category=None,
              base_date=date(2026, 5, 1)):
        for _ in range(n):
            Transaction.objects.create(
                user=user,
                account=account,
                category=category,
                amount=Decimal("100.00"),
                transaction_type=transaction_type,
                date=base_date,
            )

    def test_get_solo_del_usuario_autenticado(self, auth_a, user_a, account_a, user_b, account_b):
        self._seed(user_a, account_a, 2)
        self._seed(user_b, account_b, 5)
        response = auth_a.get(reverse("transactions:transaction-list-create"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_filtro_account_id(self, auth_a, user_a, account_a, account_a_2):
        self._seed(user_a, account_a, 3)
        self._seed(user_a, account_a_2, 2)
        response = auth_a.get(
            reverse("transactions:transaction-list-create"),
            {"account_id": account_a_2.id},
        )
        assert response.data["count"] == 2

    def test_filtro_category_id(self, auth_a, user_a, account_a, category_expense):
        self._seed(user_a, account_a, 3, category=category_expense)
        self._seed(user_a, account_a, 2, category=None)
        response = auth_a.get(
            reverse("transactions:transaction-list-create"),
            {"category_id": category_expense.id},
        )
        assert response.data["count"] == 3

    def test_filtro_transaction_type(self, auth_a, user_a, account_a):
        self._seed(user_a, account_a, 3, transaction_type="expense")
        self._seed(user_a, account_a, 2, transaction_type="income")
        response = auth_a.get(
            reverse("transactions:transaction-list-create"),
            {"transaction_type": "income"},
        )
        assert response.data["count"] == 2

    def test_filtro_date_from_date_to(self, auth_a, user_a, account_a):
        self._seed(user_a, account_a, 2, base_date=date(2026, 5, 15))  # dentro
        self._seed(user_a, account_a, 3, base_date=date(2026, 4, 10))  # fuera
        response = auth_a.get(
            reverse("transactions:transaction-list-create"),
            {"date_from": "2026-05-01", "date_to": "2026-05-31"},
        )
        assert response.data["count"] == 2

    def test_paginacion_devuelve_max_20(self, auth_a, user_a, account_a):
        self._seed(user_a, account_a, 25)
        response = auth_a.get(reverse("transactions:transaction-list-create"))
        assert response.data["count"] == 25
        assert len(response.data["results"]) == 20  # RF-011: page_size 20

    def test_get_sin_token_devuelve_401(self, client):
        response = client.get(reverse("transactions:transaction-list-create"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_aislamiento_cross_user_nunca_aparecen_ajenas(
        self, auth_a, user_a, account_a, user_b, account_b
    ):
        self._seed(user_a, account_a, 1)
        self._seed(user_b, account_b, 4)
        response = auth_a.get(reverse("transactions:transaction-list-create"))
        # Ninguna transacción devuelta pertenece a la cuenta de B
        account_ids = {t["account"] for t in response.data["results"]}
        assert account_b.id not in account_ids
        assert account_ids == {account_a.id}


# --------------------------------------------------------------------------- #
# RF-014 — endpoint de categorías
# --------------------------------------------------------------------------- #
class TestRF014Categories:
    def test_get_devuelve_200_con_categorias_del_sistema(self, auth_a):
        response = auth_a.get(reverse("categories:category-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0  # las sembradas por migración
        assert {"id", "name", "category_type", "color"} <= set(response.data[0].keys())

    def test_filtra_por_category_type(self, auth_a):
        response = auth_a.get(
            reverse("categories:category-list"), {"category_type": "income"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert all(c["category_type"] == "income" for c in response.data)

    def test_get_sin_token_devuelve_401(self, client):
        response = client.get(reverse("categories:category-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
