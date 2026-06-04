"""Integration tests del módulo AUTH con APIClient.

Cubren los criterios de aceptación de RF-001, RF-002 y RF-003 en formato
Given / When / Then. Atraviesan el stack HTTP completo (routing → view → service → DB).
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users import services

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def registered_user(db):
    """Un usuario ya registrado y activo (precondición de RF-002/RF-003)."""
    return services.create_user(
        email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
    )


# --------------------------------------------------------------------------- #
# RF-001 — Registro de usuario
# --------------------------------------------------------------------------- #
class TestRF001Registro:
    def test_registro_exitoso_devuelve_201_y_no_expone_password(self, client):
        # Given: no existe ningún usuario con el email "giuliano@zenith.app"
        url = reverse("users:register")
        payload = {
            "email": "giuliano@zenith.app",
            "name": "Giuliano",
            "password": "Tr4il-Mountain-92",
        }

        # When: se crea el usuario con nombre, email y contraseña válidos
        response = client.post(url, payload, format="json")

        # Then: el sistema responde 201 y nunca devuelve el texto plano de la contraseña
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "giuliano@zenith.app"
        assert response.data["name"] == "Giuliano"
        assert "password" not in response.data

    def test_registro_almacena_hash_y_permite_autenticarse(self, client):
        # Given / When: se registra un usuario
        client.post(
            reverse("users:register"),
            {"email": "giuliano@zenith.app", "name": "Giuliano", "password": "Tr4il-Mountain-92"},
            format="json",
        )

        # Then: el hash se almacena (no el texto plano) y puede autenticarse
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.get(email="giuliano@zenith.app")
        assert user.password != "Tr4il-Mountain-92"
        assert user.check_password("Tr4il-Mountain-92")

    def test_registro_email_duplicado_devuelve_409(self, client, registered_user):
        # Given: ya existe un usuario con ese email
        # When: se intenta registrar el mismo email
        response = client.post(
            reverse("users:register"),
            {"email": "giuliano@zenith.app", "name": "Otro", "password": "River-Bridge-77"},
            format="json",
        )
        # Then: el sistema rechaza el registro
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_registro_password_debil_devuelve_400(self, client):
        response = client.post(
            reverse("users:register"),
            {"email": "weak@zenith.app", "name": "W", "password": "123"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# --------------------------------------------------------------------------- #
# RF-002 — Login
# --------------------------------------------------------------------------- #
class TestRF002Login:
    def test_login_correcto_devuelve_200_y_token_usable(self, client, registered_user):
        # Given: un usuario registrado
        # When: envía email y contraseña correctos al endpoint de login
        response = client.post(
            reverse("users:login"),
            {"email": "giuliano@zenith.app", "password": "Tr4il-Mountain-92"},
            format="json",
        )

        # Then: responde 200 con un token de acceso válido…
        assert response.status_code == status.HTTP_200_OK
        token = response.data["token"]
        assert token

        # …y el usuario puede llamar endpoints protegidos con ese token
        protected = client.post(
            reverse("users:logout"), HTTP_AUTHORIZATION=f"Token {token}"
        )
        assert protected.status_code == status.HTTP_204_NO_CONTENT

    def test_login_password_incorrecta_devuelve_401_generico(self, client, registered_user):
        # Given: un usuario registrado
        # When: envía una contraseña incorrecta
        response = client.post(
            reverse("users:login"),
            {"email": "giuliano@zenith.app", "password": "incorrecta"},
            format="json",
        )
        # Then: responde 401 con mensaje genérico (no revela si el email existe)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "token" not in response.data

    def test_login_email_inexistente_devuelve_mismo_401(self, client):
        # El mensaje no debe distinguir email inexistente de password incorrecta.
        response = client.post(
            reverse("users:login"),
            {"email": "nadie@zenith.app", "password": "loquesea"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --------------------------------------------------------------------------- #
# RF-003 — Logout
# --------------------------------------------------------------------------- #
class TestRF003Logout:
    def _login(self, client):
        response = client.post(
            reverse("users:login"),
            {"email": "giuliano@zenith.app", "password": "Tr4il-Mountain-92"},
            format="json",
        )
        return response.data["token"]

    def test_logout_invalida_el_token(self, client, registered_user):
        # Given: un usuario con token activo
        token = self._login(client)
        auth = {"HTTP_AUTHORIZATION": f"Token {token}"}

        # When: llama al endpoint de logout con ese token
        logout = client.post(reverse("users:logout"), **auth)

        # Then: responde 200/204 y cualquier request posterior con ese token devuelve 401
        assert logout.status_code == status.HTTP_204_NO_CONTENT
        retry = client.post(reverse("users:logout"), **auth)
        assert retry.status_code == status.HTTP_401_UNAUTHORIZED

    def test_endpoint_protegido_sin_token_devuelve_401(self, client):
        # RNF-004: ruta protegida sin token → 401.
        response = client.post(reverse("users:logout"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
