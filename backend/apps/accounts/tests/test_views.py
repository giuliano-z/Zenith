"""Integration tests del módulo ACCOUNTS con APIClient.

Cubren los criterios de aceptación de RF-005, RF-006, CU-003 y CU-004 en formato
Given / When / Then. Atraviesan el stack HTTP completo (routing → view → service → DB).
Incluyen los tests de autorización cruzada exigidos por RNF-005 / RS-004.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts import services
from apps.accounts.models import AccountType, Currency

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
def auth_client_a(user_a):
    """APIClient autenticado como user_a vía Knox."""
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def auth_client_b(user_b):
    client = APIClient()
    client.force_authenticate(user=user_b)
    return client


# --------------------------------------------------------------------------- #
# RF-005 — Crear cuenta
# --------------------------------------------------------------------------- #
class TestRF005CrearCuenta:
    def test_post_account_valido_devuelve_201(self, auth_client_a):
        # Given: un usuario autenticado
        # When: POST con un payload válido
        response = auth_client_a.post(
            reverse("accounts:account-list-create"),
            {
                "name": "Mercado Pago",
                "account_type": "digital_wallet",
                "currency": "ARS",
                "initial_balance": 5000,
            },
            format="json",
        )
        # Then: 201 con la cuenta creada y su balance
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Mercado Pago"
        assert response.data["account_type"] == "digital_wallet"
        assert response.data["currency"] == "ARS"
        assert Decimal(str(response.data["balance"])) == Decimal("5000.00")

    def test_cuenta_creada_aparece_en_lista_y_no_para_otro_usuario(
        self, auth_client_a, auth_client_b
    ):
        # Criterio literal RF-005: tras crearla, aparece en GET propio con balance 5000
        # y NO es visible para el otro usuario.
        auth_client_a.post(
            reverse("accounts:account-list-create"),
            {
                "name": "Mercado Pago",
                "account_type": "digital_wallet",
                "currency": "ARS",
                "initial_balance": 5000,
            },
            format="json",
        )
        lista_a = auth_client_a.get(reverse("accounts:account-list-create"))
        assert lista_a.status_code == status.HTTP_200_OK
        assert len(lista_a.data) == 1
        assert Decimal(str(lista_a.data[0]["balance"])) == Decimal("5000.00")

        lista_b = auth_client_b.get(reverse("accounts:account-list-create"))
        assert lista_b.data == []

    def test_post_account_sin_token_devuelve_401(self, client):
        response = client.post(
            reverse("accounts:account-list-create"),
            {"name": "X", "account_type": "cash", "currency": "ARS"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_account_type_invalido_devuelve_400(self, auth_client_a):
        response = auth_client_a.post(
            reverse("accounts:account-list-create"),
            {"name": "X", "account_type": "cripto", "currency": "ARS"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_currency_invalida_devuelve_400(self, auth_client_a):
        response = auth_client_a.post(
            reverse("accounts:account-list-create"),
            {"name": "X", "account_type": "cash", "currency": "EUR"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# --------------------------------------------------------------------------- #
# RF-006 — Listar cuentas
# --------------------------------------------------------------------------- #
class TestRF006ListarCuentas:
    def test_get_accounts_propias_devuelve_200(self, auth_client_a, user_a):
        # Given: un usuario con 3 cuentas activas (mix ARS y USD)
        services.create_account(
            user=user_a, name="Caja", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("10000"),
        )
        services.create_account(
            user=user_a, name="MP", account_type=AccountType.DIGITAL_WALLET,
            currency=Currency.ARS, initial_balance=Decimal("5000"),
        )
        services.create_account(
            user=user_a, name="Banco", account_type=AccountType.BANK,
            currency=Currency.USD, initial_balance=Decimal("100"),
        )
        # When: GET /api/accounts/
        response = auth_client_a.get(reverse("accounts:account-list-create"))
        # Then: 200 con exactamente esas 3 cuentas
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_get_accounts_aislamiento_entre_usuarios(
        self, auth_client_a, user_a, user_b
    ):
        # Given: una cuenta de A y una de B
        services.create_account(
            user=user_a, name="De A", account_type=AccountType.CASH, currency=Currency.ARS
        )
        services.create_account(
            user=user_b, name="De B", account_type=AccountType.CASH, currency=Currency.ARS
        )
        # When: A lista sus cuentas
        response = auth_client_a.get(reverse("accounts:account-list-create"))
        # Then: solo ve la suya; la de B NO aparece (RNF-005)
        assert response.status_code == status.HTTP_200_OK
        names = [item["name"] for item in response.data]
        assert names == ["De A"]


# --------------------------------------------------------------------------- #
# CU-003 — Detalle de cuenta
# --------------------------------------------------------------------------- #
class TestCU003DetalleCuenta:
    def test_get_account_detail_propia_devuelve_200(self, auth_client_a, user_a):
        account = services.create_account(
            user=user_a, name="Mía", account_type=AccountType.CASH, currency=Currency.ARS
        )
        response = auth_client_a.get(
            reverse("accounts:account-detail", args=[account.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == account.id

    def test_get_account_detail_ajena_devuelve_403_nunca_404(
        self, auth_client_b, user_a
    ):
        # Given: una cuenta de A; B intenta verla (autorización cruzada, RS-004)
        account = services.create_account(
            user=user_a, name="De A", account_type=AccountType.CASH, currency=Currency.ARS
        )
        # When: B pide el detalle
        response = auth_client_b.get(
            reverse("accounts:account-detail", args=[account.id])
        )
        # Then: 403, NUNCA 404 (un 404 confirmaría la existencia del recurso)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_get_account_detail_sin_token_devuelve_401(self, client, user_a):
        account = services.create_account(
            user=user_a, name="Mía", account_type=AccountType.CASH, currency=Currency.ARS
        )
        response = client.get(reverse("accounts:account-detail", args=[account.id]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --------------------------------------------------------------------------- #
# CU-004 — Balance consolidado por moneda
# --------------------------------------------------------------------------- #
class TestCU004BalanceConsolidado:
    def test_get_balance_ars_y_usd_devuelve_200_totales_correctos(
        self, auth_client_a, user_a
    ):
        # Given: cuentas ARS (total 15000) y USD (total 100)
        services.create_account(
            user=user_a, name="Caja", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("10000"),
        )
        services.create_account(
            user=user_a, name="MP", account_type=AccountType.DIGITAL_WALLET,
            currency=Currency.ARS, initial_balance=Decimal("5000"),
        )
        services.create_account(
            user=user_a, name="Banco", account_type=AccountType.BANK,
            currency=Currency.USD, initial_balance=Decimal("100"),
        )
        # When: GET /api/accounts/balance/
        response = auth_client_a.get(reverse("accounts:account-balance"))
        # Then: 200 con los totales por moneda
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(str(response.data["ARS"])) == Decimal("15000.00")
        assert Decimal(str(response.data["USD"])) == Decimal("100.00")

    def test_get_balance_solo_cuentas_activas_del_usuario(
        self, auth_client_a, user_a, user_b
    ):
        # Una activa propia, una inactiva propia, una de otro usuario.
        services.create_account(
            user=user_a, name="Activa", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("1000"),
        )
        inactiva = services.create_account(
            user=user_a, name="Archivada", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("9999"),
        )
        inactiva.is_active = False
        inactiva.save()
        services.create_account(
            user=user_b, name="Ajena", account_type=AccountType.CASH,
            currency=Currency.ARS, initial_balance=Decimal("8888"),
        )

        response = auth_client_a.get(reverse("accounts:account-balance"))
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(str(response.data["ARS"])) == Decimal("1000.00")

    def test_get_balance_sin_token_devuelve_401(self, client):
        response = client.get(reverse("accounts:account-balance"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
