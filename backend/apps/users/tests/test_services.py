"""Unit tests de la capa de dominio (services.py).

No instancian el stack HTTP: prueban la lógica de negocio directamente (RNF-006).
Necesitan DB porque User persiste; se marcan con django_db.
"""
import pytest
from django.contrib.auth import get_user_model

from apps.users import services
from apps.users.services import (
    DjangoValidationError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestCreateUser:
    def test_crea_usuario_con_password_hasheada(self):
        user = services.create_user(
            email="giuliano@zenith.app", name="Giuliano", password="Tr4il-Mountain-92"
        )
        assert user.pk is not None
        assert user.email == "giuliano@zenith.app"
        assert user.name == "Giuliano"
        # RF-001: nunca se almacena el texto plano.
        assert user.password != "Tr4il-Mountain-92"
        assert user.check_password("Tr4il-Mountain-92")

    def test_normaliza_dominio_del_email(self):
        user = services.create_user(
            email="Giuliano@ZENITH.APP", name="Giuliano", password="Tr4il-Mountain-92"
        )
        assert user.email == "Giuliano@zenith.app"  # normalize_email solo baja el dominio

    def test_email_duplicado_lanza_error(self):
        services.create_user(email="dup@zenith.app", name="A", password="Tr4il-Mountain-92")
        with pytest.raises(EmailAlreadyExistsError):
            services.create_user(email="dup@zenith.app", name="B", password="River-Bridge-77")

    def test_email_duplicado_es_case_insensitive(self):
        services.create_user(email="dup@zenith.app", name="A", password="Tr4il-Mountain-92")
        with pytest.raises(EmailAlreadyExistsError):
            services.create_user(email="DUP@zenith.app", name="B", password="River-Bridge-77")

    def test_password_debil_lanza_validation_error(self):
        with pytest.raises(DjangoValidationError):
            services.create_user(email="weak@zenith.app", name="W", password="123")
        assert not User.objects.filter(email="weak@zenith.app").exists()


class TestAuthenticateUser:
    def test_credenciales_correctas_devuelve_usuario(self):
        services.create_user(email="ana@zenith.app", name="Ana", password="Tr4il-Mountain-92")
        user = services.authenticate_user(email="ana@zenith.app", password="Tr4il-Mountain-92")
        assert user.email == "ana@zenith.app"

    def test_password_incorrecta_lanza_invalid_credentials(self):
        services.create_user(email="ana@zenith.app", name="Ana", password="Tr4il-Mountain-92")
        with pytest.raises(InvalidCredentialsError):
            services.authenticate_user(email="ana@zenith.app", password="incorrecta")

    def test_email_inexistente_lanza_invalid_credentials(self):
        # Mismo error que password incorrecta: no se revela si el email existe (RS-002).
        with pytest.raises(InvalidCredentialsError):
            services.authenticate_user(email="nadie@zenith.app", password="loquesea")

    def test_usuario_inactivo_no_autentica(self):
        user = services.create_user(
            email="off@zenith.app", name="Off", password="Tr4il-Mountain-92"
        )
        user.is_active = False
        user.save()
        with pytest.raises(InvalidCredentialsError):
            services.authenticate_user(email="off@zenith.app", password="Tr4il-Mountain-92")


class TestUserManager:
    def test_create_user_sin_email_falla(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", name="X", password="Tr4il-Mountain-92")

    def test_create_superuser_marca_flags(self):
        admin = User.objects.create_superuser(
            email="admin@zenith.app", name="Admin", password="Tr4il-Mountain-92"
        )
        assert admin.is_staff
        assert admin.is_superuser
