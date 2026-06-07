"""Unit tests de la capa de dominio (domain/services.py) del módulo DASHBOARD.

Prueban la agregación directamente, sin stack HTTP (RNF-006). Necesitan DB
(crean cuentas, transacciones y tasas), así que se marcan con django_db. Los
datos se siembran vía los servicios de dominio reales de cada módulo, no a mano.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import AccountType, Currency
from apps.accounts.services import create_account
from apps.currency.models import ExchangeRate, RateType, Source
from apps.dashboard.domain import services
from apps.transactions.models import Category
from apps.transactions.services import create_transaction, create_transfer

User = get_user_model()

pytestmark = pytest.mark.django_db

YEAR, MONTH = 2026, 6


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
    )


@pytest.fixture
def account_ars(user):
    return create_account(
        user=user,
        name="Caja ARS",
        account_type=AccountType.CASH,
        currency=Currency.ARS,
        initial_balance=Decimal("0"),
    )


@pytest.fixture
def account_ars_2(user):
    return create_account(
        user=user,
        name="Banco ARS",
        account_type=AccountType.BANK,
        currency=Currency.ARS,
        initial_balance=Decimal("0"),
    )


@pytest.fixture
def account_usd(user):
    return create_account(
        user=user,
        name="Caja USD",
        account_type=AccountType.CASH,
        currency=Currency.USD,
        initial_balance=Decimal("0"),
    )


@pytest.fixture
def cat_alimentacion(db):
    return Category.objects.create(
        name="Alimentación", category_type=Category.CategoryType.EXPENSE, is_default=True
    )


@pytest.fixture
def cat_transporte(db):
    return Category.objects.create(
        name="Transporte", category_type=Category.CategoryType.EXPENSE, is_default=True
    )


def _income(user, account, amount, day=5):
    return create_transaction(
        user=user,
        account_id=account.id,
        amount=Decimal(amount),
        transaction_type="income",
        date=date(YEAR, MONTH, day),
    )


def _expense(user, account, amount, category=None, day=5):
    return create_transaction(
        user=user,
        account_id=account.id,
        amount=Decimal(amount),
        transaction_type="expense",
        date=date(YEAR, MONTH, day),
        category_id=category.id if category else None,
    )


# --------------------------------------------------------------------------- #
# get_period_summary
# --------------------------------------------------------------------------- #
class TestGetPeriodSummary:
    def test_vacio_si_no_hay_transacciones(self, user, account_ars):
        assert services.get_period_summary(user, YEAR, MONTH) == {}

    def test_agrupa_por_moneda(self, user, account_ars, account_usd):
        _income(user, account_ars, "80000")
        _expense(user, account_ars, "55000")
        _expense(user, account_usd, "200")

        summary = services.get_period_summary(user, YEAR, MONTH)

        assert summary["ARS"]["income"] == Decimal("80000")
        assert summary["ARS"]["expenses"] == Decimal("55000")
        assert summary["ARS"]["net"] == Decimal("25000")
        assert summary["USD"]["income"] == Decimal("0")
        assert summary["USD"]["expenses"] == Decimal("200")
        assert summary["USD"]["net"] == Decimal("-200")

    def test_no_incluye_transfers(self, user, account_ars, account_ars_2):
        _income(user, account_ars, "10000")
        create_transfer(
            user=user,
            from_account_id=account_ars.id,
            to_account_id=account_ars_2.id,
            amount=Decimal("3000"),
            date=date(YEAR, MONTH, 6),
        )

        summary = services.get_period_summary(user, YEAR, MONTH)

        # Solo el ingreso cuenta; ni transfer_out ni transfer_in aparecen.
        assert summary["ARS"]["income"] == Decimal("10000")
        assert summary["ARS"]["expenses"] == Decimal("0")

    def test_solo_transacciones_del_periodo(self, user, account_ars):
        _income(user, account_ars, "5000")
        create_transaction(
            user=user,
            account_id=account_ars.id,
            amount=Decimal("9999"),
            transaction_type="income",
            date=date(YEAR, MONTH - 1, 15),
        )

        summary = services.get_period_summary(user, YEAR, MONTH)
        assert summary["ARS"]["income"] == Decimal("5000")


# --------------------------------------------------------------------------- #
# get_expenses_by_category
# --------------------------------------------------------------------------- #
class TestGetExpensesByCategory:
    def test_ordenadas_por_monto_desc(
        self, user, account_ars, cat_alimentacion, cat_transporte
    ):
        _expense(user, account_ars, "5000", cat_transporte)
        _expense(user, account_ars, "20000", cat_alimentacion)

        rows = services.get_expenses_by_category(user, YEAR, MONTH)

        assert [r["category_name"] for r in rows] == ["Alimentación", "Transporte"]

    def test_calcula_porcentajes(
        self, user, account_ars, cat_alimentacion, cat_transporte
    ):
        _expense(user, account_ars, "30000", cat_alimentacion)
        _expense(user, account_ars, "10000", cat_transporte)

        rows = services.get_expenses_by_category(user, YEAR, MONTH)

        by_name = {r["category_name"]: r for r in rows}
        assert by_name["Alimentación"]["percentage"] == Decimal("75.00")
        assert by_name["Transporte"]["percentage"] == Decimal("25.00")


# --------------------------------------------------------------------------- #
# get_consolidated_ars
# --------------------------------------------------------------------------- #
class TestGetConsolidatedArs:
    def test_none_si_no_hay_tc(self, user):
        summary = {
            "ARS": {"income": Decimal("100"), "expenses": Decimal("0"), "net": Decimal("100")}
        }
        assert services.get_consolidated_ars(summary, []) is None

    def test_convierte_con_tc(self, user):
        ExchangeRate.objects.create(
            rate=Decimal("1380.0000"),
            rate_type=RateType.BLUE,
            effective_date=date(YEAR, MONTH, 6),
            source=Source.MANUAL,
            created_by=user,
        )
        summary = {
            "ARS": {
                "income": Decimal("80000"),
                "expenses": Decimal("55000"),
                "net": Decimal("25000"),
            },
            "USD": {
                "income": Decimal("0"),
                "expenses": Decimal("200"),
                "net": Decimal("-200"),
            },
        }

        result = services.get_consolidated_ars(summary, [])

        # 80000 + 0*1380 = 80000 income; 55000 + 200*1380 = 331000 expenses
        assert result["income"] == Decimal("80000")
        assert result["expenses"] == Decimal("331000")
        assert result["net"] == Decimal("-251000")
        assert result["rate_used"] == Decimal("1380.0000")
        assert result["rate_type"] == "blue"
        assert result["rate_date"] == date(YEAR, MONTH, 6)
