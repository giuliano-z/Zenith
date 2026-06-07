"""Unit tests de la capa de dominio (services.py) del módulo SHARED.

Prueban la lógica de negocio directamente, sin stack HTTP (RNF-006). Necesitan DB
(crean usuarios, cuentas, transacciones y gastos compartidos), así que se marcan
con django_db. El sistema se diseñó para dos usuarios: las fixtures crean
exactamente dos usuarios activos.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import AccountType, Currency
from apps.accounts.services import create_account
from apps.shared import services
from apps.shared.models import SharedExpense, SharedSettlement
from apps.transactions.models import Transaction

User = get_user_model()

pytestmark = pytest.mark.django_db

TODAY = date(2026, 6, 7)


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
def account_b(user_b):
    return create_account(
        user=user_b,
        name="Caja B",
        account_type=AccountType.CASH,
        currency=Currency.ARS,
        initial_balance=Decimal("0"),
    )


def _expense(payer, account, *, total, debtor, created_by=None):
    return services.create_shared_expense(
        payer=payer,
        account_id=account.id,
        total_amount=Decimal(total),
        debtor_amount=Decimal(debtor),
        currency=Currency.ARS,
        date=TODAY,
        description="Cena",
        created_by=created_by or payer,
    )


# --------------------------------------------------------------------------- #
# create_shared_expense
# --------------------------------------------------------------------------- #
class TestCreateSharedExpense:
    def test_crea_transaction_y_shared_expense(self, user_a, user_b, account_a):
        expense = _expense(user_a, account_a, total="10000", debtor="5000")

        assert SharedExpense.objects.count() == 1
        assert expense.payer == user_a
        assert expense.debtor == user_b
        assert expense.debtor_amount == Decimal("5000")
        # La Transaction es expense por el total, en la cuenta del pagador.
        assert expense.transaction.transaction_type == Transaction.TransactionType.EXPENSE
        assert expense.transaction.amount == Decimal("10000")
        assert expense.transaction.account_id == account_a.id

    def test_falla_si_cuenta_no_es_del_payer(self, user_a, user_b, account_b):
        # account_b es de user_b; user_a no puede usarla → 403.
        with pytest.raises(services.AccountAccessDeniedError):
            _expense(user_a, account_b, total="10000", debtor="5000")
        # Atómico: no se creó ni la transacción ni el gasto.
        assert SharedExpense.objects.count() == 0
        assert Transaction.objects.count() == 0

    def test_falla_si_moneda_no_coincide(self, user_a, user_b):
        account_usd = create_account(
            user=user_a,
            name="Caja USD",
            account_type=AccountType.CASH,
            currency=Currency.USD,
            initial_balance=Decimal("0"),
        )
        with pytest.raises(services.SharedValidationError):
            services.create_shared_expense(
                payer=user_a,
                account_id=account_usd.id,
                total_amount=Decimal("100"),
                debtor_amount=Decimal("50"),
                currency=Currency.ARS,
                date=TODAY,
                description="Cena",
                created_by=user_a,
            )


# --------------------------------------------------------------------------- #
# get_shared_balance
# --------------------------------------------------------------------------- #
class TestGetSharedBalance:
    def test_is_balanced_sin_unsettled(self, user_a, user_b):
        balance = services.get_shared_balance()
        assert balance["is_balanced"] is True
        assert balance["net_amount"] == Decimal("0")
        assert balance["creditor"] is None and balance["debtor"] is None

    def test_net_solo_a_pago(self, user_a, user_b, account_a):
        _expense(user_a, account_a, total="10000", debtor="5000")

        balance = services.get_shared_balance()
        assert balance["is_balanced"] is False
        assert balance["net_amount"] == Decimal("5000")
        assert balance["creditor"] == user_a
        assert balance["debtor"] == user_b

    def test_compensacion(self, user_a, user_b, account_a, account_b):
        # A pagó y B le debe 10k; B pagó y A le debe 3k → neto: B le debe 7k a A.
        _expense(user_a, account_a, total="20000", debtor="10000")
        _expense(user_b, account_b, total="6000", debtor="3000")

        balance = services.get_shared_balance()
        assert balance["net_amount"] == Decimal("7000")
        assert balance["creditor"] == user_a
        assert balance["debtor"] == user_b


# --------------------------------------------------------------------------- #
# settle_shared_balance
# --------------------------------------------------------------------------- #
class TestSettleSharedBalance:
    def test_marca_todos_settled(self, user_a, user_b, account_a):
        _expense(user_a, account_a, total="10000", debtor="5000")
        _expense(user_a, account_a, total="4000", debtor="2000")

        services.settle_shared_balance(settled_by=user_a)

        assert SharedExpense.objects.filter(is_settled=False).count() == 0
        assert SharedExpense.objects.filter(is_settled=True).count() == 2

    def test_crea_settlement_con_snapshot(self, user_a, user_b, account_a):
        _expense(user_a, account_a, total="10000", debtor="5000")

        settlement = services.settle_shared_balance(settled_by=user_a)

        assert SharedSettlement.objects.count() == 1
        assert settlement.net_amount == Decimal("5000")
        assert settlement.creditor == user_a
        assert settlement.debtor == user_b
        assert settlement.settled_by == user_a
        assert settlement.transfer_out is None  # sin cuentas → sin pago

    def test_con_transferencia_valida_ownership_y_crea_par(
        self, user_a, user_b, account_a, account_b
    ):
        _expense(user_a, account_a, total="10000", debtor="5000")

        # Deudor = user_b paga desde account_b hacia account_a del acreedor.
        settlement = services.settle_shared_balance(
            settled_by=user_b,
            from_account_id=account_b.id,
            to_account_id=account_a.id,
        )

        assert settlement.transfer_out is not None
        assert settlement.transfer_in is not None
        assert settlement.transfer_out.account_id == account_b.id
        assert settlement.transfer_in.account_id == account_a.id
        assert settlement.transfer_out.amount == Decimal("5000")

    def test_retorna_none_si_balanced(self, user_a, user_b):
        assert services.settle_shared_balance(settled_by=user_a) is None
