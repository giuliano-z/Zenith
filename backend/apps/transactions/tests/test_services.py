"""Unit tests de la capa de dominio (services.py) del módulo TRANSACTIONS.

Prueban la lógica de negocio directamente, sin stack HTTP (RNF-006), salvo el test de
integración ADR-004 (test_balance_cuenta_integra_transactions), que SÍ atraviesa el
endpoint de accounts para verificar que el balance refleja las nuevas transacciones.
Necesitan DB: se marcan con django_db.
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
from apps.transactions import services
from apps.transactions.models import Category, Transaction

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="ana@zenith.app", name="Ana", password="River-Bridge-77"
    )


@pytest.fixture
def account_ars(user):
    return create_account(
        user=user,
        name="Caja ARS",
        account_type=AccountType.CASH,
        currency=Currency.ARS,
        initial_balance=Decimal("10000.00"),
    )


@pytest.fixture
def account_ars_2(user):
    return create_account(
        user=user,
        name="MP ARS",
        account_type=AccountType.DIGITAL_WALLET,
        currency=Currency.ARS,
        initial_balance=Decimal("5000.00"),
    )


# --------------------------------------------------------------------------- #
# get_transaction_sum_for_account (ADR-004)
# --------------------------------------------------------------------------- #
class TestTransactionSum:
    def test_income_aumenta_transaction_sum(self, user, account_ars):
        # Given: una cuenta sin transacciones (suma 0)
        assert services.get_transaction_sum_for_account(account_ars.id) == Decimal("0")
        # When: se registra un income de 2000
        services.create_transaction(
            user=user,
            account_id=account_ars.id,
            amount=Decimal("2000.00"),
            transaction_type=Transaction.TransactionType.INCOME,
            date=date(2026, 6, 1),
        )
        # Then: la suma neta sube en 2000
        assert services.get_transaction_sum_for_account(account_ars.id) == Decimal("2000.00")

    def test_expense_reduce_transaction_sum(self, user, account_ars):
        # When: un expense de 2000
        services.create_transaction(
            user=user,
            account_id=account_ars.id,
            amount=Decimal("2000.00"),
            transaction_type=Transaction.TransactionType.EXPENSE,
            date=date(2026, 6, 1),
        )
        # Then: la suma neta baja en 2000
        assert services.get_transaction_sum_for_account(account_ars.id) == Decimal("-2000.00")

    def test_transfer_out_reduce_origen_transfer_in_aumenta_destino(
        self, user, account_ars, account_ars_2
    ):
        # When: transferencia de 3000 de la cuenta 1 a la 2
        services.create_transfer(
            user=user,
            from_account_id=account_ars.id,
            to_account_id=account_ars_2.id,
            amount=Decimal("3000.00"),
            date=date(2026, 6, 1),
        )
        # Then: origen -3000, destino +3000
        assert services.get_transaction_sum_for_account(account_ars.id) == Decimal("-3000.00")
        assert services.get_transaction_sum_for_account(account_ars_2.id) == Decimal("3000.00")

    def test_cuota_future_excluida_del_balance(self, user, account_ars):
        # Given: installment de 60000 en 3 cuotas desde 01/06/2026
        services.create_installment(
            user=user,
            account_id=account_ars.id,
            total_amount=Decimal("60000.00"),
            installment_count=3,
            first_installment_date=date(2026, 6, 1),
        )
        # When: el corte es 15/06/2026 (solo la 1ª cuota ya venció)
        suma = services.get_transaction_sum_for_account(
            account_ars.id, as_of_date=date(2026, 6, 15)
        )
        # Then: solo impacta la cuota de junio (-20000); julio y agosto son futuras
        assert suma == Decimal("-20000.00")

    def test_transaction_inactiva_no_impacta_balance(self, user, account_ars):
        # Given: un expense que luego se marca inactivo
        tx = services.create_transaction(
            user=user,
            account_id=account_ars.id,
            amount=Decimal("2000.00"),
            transaction_type=Transaction.TransactionType.EXPENSE,
            date=date(2026, 6, 1),
        )
        tx.is_active = False
        tx.save()
        # Then: no impacta la suma neta
        assert services.get_transaction_sum_for_account(account_ars.id) == Decimal("0")


# --------------------------------------------------------------------------- #
# create_installment (RF-010)
# --------------------------------------------------------------------------- #
class TestInstallment:
    def test_installment_amount_per_cuota_es_total_dividido_count(self, user, account_ars):
        purchase = services.create_installment(
            user=user,
            account_id=account_ars.id,
            total_amount=Decimal("60000.00"),
            installment_count=3,
            first_installment_date=date(2026, 6, 1),
        )
        assert purchase.amount_per_installment == Decimal("20000.00")

    def test_installment_genera_N_transactions(self, user, account_ars):
        purchase = services.create_installment(
            user=user,
            account_id=account_ars.id,
            total_amount=Decimal("60000.00"),
            installment_count=3,
            first_installment_date=date(2026, 6, 1),
        )
        txs = purchase.transactions.all()
        assert txs.count() == 3
        assert all(t.amount == Decimal("20000.00") for t in txs)
        assert all(
            t.transaction_type == Transaction.TransactionType.EXPENSE for t in txs
        )

    def test_installment_fechas_son_mensuales(self, user, account_ars):
        purchase = services.create_installment(
            user=user,
            account_id=account_ars.id,
            total_amount=Decimal("60000.00"),
            installment_count=3,
            first_installment_date=date(2026, 6, 1),
        )
        fechas = sorted(t.date for t in purchase.transactions.all())
        assert fechas == [date(2026, 6, 1), date(2026, 7, 1), date(2026, 8, 1)]


# --------------------------------------------------------------------------- #
# RF-014 — listado de categorías (list_categories)
# --------------------------------------------------------------------------- #
class TestRF014ListCategories:
    def test_incluye_categorias_del_sistema(self, user):
        # Given: categorías del sistema sembradas por migración (user=None)
        # When: el usuario lista categorías
        result = services.list_categories(user=user)
        # Then: ve las del sistema
        assert result.count() > 0
        assert all(c.user_id is None for c in result)

    def test_filtra_por_category_type(self, user):
        result = services.list_categories(user=user, category_type="income")
        assert result.count() > 0
        assert all(c.category_type == "income" for c in result)

    def test_no_ve_categorias_privadas_de_otro_usuario(self, user, other_user):
        # Given: other_user tiene una categoría propia
        ajena = Category.objects.create(
            name="Categoría privada de Ana",
            category_type="expense",
            user=other_user,
        )
        # When: user lista sus categorías
        result = services.list_categories(user=user)
        # Then: no aparece la ajena (RNF-005)
        assert ajena.id not in [c.id for c in result]

    def test_incluye_categorias_propias(self, user):
        propia = Category.objects.create(
            name="Categoría propia", category_type="expense", user=user
        )
        result = services.list_categories(user=user)
        assert propia.id in [c.id for c in result]


# --------------------------------------------------------------------------- #
# ADR-004 — integración con el balance de la cuenta (vía endpoint de accounts)
# --------------------------------------------------------------------------- #
class TestBalanceIntegraTransactions:
    def test_balance_cuenta_integra_transactions(self, user, account_ars):
        # Given: cuenta ARS con balance inicial 10000 y un expense de 2000 (hoy o antes)
        services.create_transaction(
            user=user,
            account_id=account_ars.id,
            amount=Decimal("2000.00"),
            transaction_type=Transaction.TransactionType.EXPENSE,
            date=date(2020, 1, 1),  # pasado: seguro <= hoy
        )
        client = APIClient()
        client.force_authenticate(user=user)
        # When: GET /api/accounts/{id}/
        response = client.get(reverse("accounts:account-detail", args=[account_ars.id]))
        # Then: el balance refleja initial_balance + suma de transactions = 8000 (ADR-004)
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(str(response.data["balance"])) == Decimal("8000.00")
