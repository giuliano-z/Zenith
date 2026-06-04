"""Lógica de negocio del módulo AUTH (capa de dominio).

No depende de HTTP: ninguna función recibe un Request. Es testeable en aislamiento
(RNF-006). Las vistas y serializers consumen estas funciones.
"""
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

User = get_user_model()


class EmailAlreadyExistsError(Exception):
    """El email ya está registrado (RF-001, precondición violada)."""


class InvalidCredentialsError(Exception):
    """Credenciales inválidas. Mensaje genérico: no revela si el email existe (RF-002)."""


def create_user(*, email: str, name: str, password: str) -> User:
    """Crea un usuario con contraseña hasheada (RF-001).

    Valida la fortaleza de la contraseña con los validators de Django y la unicidad
    del email. Lanza EmailAlreadyExistsError o DjangoValidationError ante fallos.
    """
    email = User.objects.normalize_email(email)
    if User.objects.filter(email__iexact=email).exists():
        raise EmailAlreadyExistsError(email)

    user = User(email=email, name=name)
    user.set_password(password)
    validate_password(password, user)
    try:
        user.save()
    except IntegrityError as exc:  # carrera entre el check y el save
        raise EmailAlreadyExistsError(email) from exc
    return user


def authenticate_user(*, email: str, password: str) -> User:
    """Autentica por email + contraseña (RF-002).

    Devuelve el usuario si las credenciales son válidas y la cuenta está activa.
    Ante cualquier fallo lanza InvalidCredentialsError con mensaje genérico, sin
    distinguir entre email inexistente y contraseña incorrecta (RS-002 / no enumeración).
    """
    email = User.objects.normalize_email(email)
    user = authenticate(username=email, password=password)
    if user is None or not user.is_active:
        raise InvalidCredentialsError()
    return user


__all__ = [
    "EmailAlreadyExistsError",
    "InvalidCredentialsError",
    "DjangoValidationError",
    "create_user",
    "authenticate_user",
]
