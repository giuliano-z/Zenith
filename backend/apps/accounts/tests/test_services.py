"""Unit tests de la capa de dominio (models + services.py) del módulo ACCOUNTS.

No instancian el stack HTTP: prueban la entidad y la lógica de negocio directamente
(RNF-006). Necesitan DB porque Account persiste; se marcan con django_db.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.accounts import services
from apps.accounts.models import Account, AccountType, Currency
from apps.accounts.services import AccountAccessDeniedError, AccountNotFoundError

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


# --------------------------------------------------------------------------- #
# Entidad Account
# --------------------------------------------------------------------------- #
class TestAccountEntity:
    def test_account_entity_valid_creation(self, user):
        # Given/When: una cuenta con valores válidos
        account = Account(
            user=user,
            name="Mercado Pago",
            account_type=AccountType.DIGITAL_WALLET,
            currency=Currency.ARS,
            initial_balance=Decimal("5000.00"),
        )
        account.full_clean()  # no lanza
        account.save()

        # Then: persiste con sus valores y defaults
        assert account.pk is not None
        assert account.is_active is True
        assert account.created_at is not None

    def test_account_entity_invalid_type(self, user):
        # Given: un account_type fuera del enum
        account = Account(
            user=user,
            name="Rara",
            account_type="cripto",
            currency=Currency.ARS,
            initial_balance=Decimal("0"),
        )
        # Then: full_clean rechaza el valor
        with pytest.raises(ValidationError):
            account.full_clean()

    def test_account_entity_invalid_currency(self, user):
        # Given: una currency fuera del enum
        account = Account(
            user=user,
            name="Rara",
            account_type=AccountType.CASH,
            currency="EUR",
            initial_balance=Decimal("0"),
        )
        # Then: full_clean rechaza el valor
        with pytest.raises(ValidationError):
            account.full_clean()


# --------------------------------------------------------------------------- #
# Balance (ADR-004)
# --------------------------------------------------------------------------- #
class TestBalance:
    def test_balance_equals_initial_when_no_transactions(self, user):
        # Given: una cuenta sin transacciones (TRANSACTIONS aún no existe)
        account = services.create_account(
            user=user,
            name="Efectivo",
            account_type=AccountType.CASH,
            currency=Currency.ARS,
            initial_balance=Decimal("1500.00"),
        )
        # When/Then: el balance es exactamente el saldo inicial
        assert services.get_balance(account) == Decimal("1500.00")

    def test_get_balance_suma_transacciones_cuando_se_inyectan(self, user):
        # ADR-004: cuando F4 pase la suma real, el balance la incorpora sin tocar la firma.
        account = services.create_account(
            user=user,
            name="Banco",
            account_type=AccountType.BANK,
            currency=Currency.ARS,
            initial_balance=Decimal("1000.00"),
        )
        assert services.get_balance(account, Decimal("250.50")) == Decimal("1250.50")


# --------------------------------------------------------------------------- #
# Servicios
# --------------------------------------------------------------------------- #
class TestCreateAccount:
    def test_create_account_asigna_owner(self, user):
        account = services.create_account(
            user=user,
            name="Mercado Pago",
            account_type=AccountType.DIGITAL_WALLET,
            currency=Currency.ARS,
        )
        assert account.user_id == user.id
        assert account.initial_balance == Decimal("0")  # default


class TestGetAccounts:
    def test_get_accounts_solo_devuelve_las_del_user(self, user, other_user):
        services.create_account(
            user=user, name="Mía", account_type=AccountType.CASH, currency=Currency.ARS
        )
        services.create_account(
            user=other_user, name="Ajena", account_type=AccountType.CASH, currency=Currency.ARS
        )
        accounts = services.get_accounts(user=user)
        assert accounts.count() == 1
        assert accounts.first().name == "Mía"

    def test_get_accounts_excluye_inactivas(self, user):
        services.create_account(
            user=user, name="Activa", account_type=AccountType.CASH, currency=Currency.ARS
        )
        inactiva = services.create_account(
            user=user, name="Archivada", account_type=AccountType.CASH, currency=Currency.ARS
        )
        inactiva.is_active = False
        inactiva.save()

        accounts = services.get_accounts(user=user)
        assert accounts.count() == 1
        assert accounts.first().name == "Activa"


class TestGetAccountDetail:
    def test_get_account_detail_propia_devuelve_cuenta(self, user):
        account = services.create_account(
            user=user, name="Mía", account_type=AccountType.CASH, currency=Currency.ARS
        )
        assert services.get_account_detail(user=user, account_id=account.id) == account

    def test_get_account_detail_ajena_lanza_access_denied(self, user, other_user):
        ajena = services.create_account(
            user=other_user, name="Ajena", account_type=AccountType.CASH, currency=Currency.ARS
        )
        # RS-004: cuenta de otro → AccessDenied (la view lo traduce a 403), nunca NotFound.
        with pytest.raises(AccountAccessDeniedError):
            services.get_account_detail(user=user, account_id=ajena.id)

    def test_get_account_detail_inexistente_lanza_not_found(self, user):
        with pytest.raises(AccountNotFoundError):
            services.get_account_detail(user=user, account_id=999999)


class TestGetBalanceByCurrency:
    def test_get_balance_by_currency_suma_por_moneda_solo_activas(self, user, other_user):
        # Cuentas ARS: 10000 + 5000 = 15000
        services.create_account(
            user=user, name="Caja ARS", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("10000"),
        )
        services.create_account(
            user=user, name="MP ARS", account_type=AccountType.DIGITAL_WALLET,
            currency=Currency.ARS, initial_balance=Decimal("5000"),
        )
        # Cuenta USD: 100
        services.create_account(
            user=user, name="Banco USD", account_type=AccountType.BANK,
            currency=Currency.USD, initial_balance=Decimal("100"),
        )
        # Una inactiva: NO debe contar
        inactiva = services.create_account(
            user=user, name="Vieja ARS", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("99999"),
        )
        inactiva.is_active = False
        inactiva.save()
        # Una de otro usuario: NO debe contar
        services.create_account(
            user=other_user, name="Ajena ARS", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("88888"),
        )

        totals = services.get_balance_by_currency(user=user)
        assert totals == {"ARS": Decimal("15000"), "USD": Decimal("100")}
