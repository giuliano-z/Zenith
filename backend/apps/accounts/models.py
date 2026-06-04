"""Modelo de dominio Account (RF-005).

Una cuenta pertenece a un único usuario y nunca cambia de propietario. El balance
NO se almacena: se calcula en tiempo real (ADR-004) en la capa de servicio. Los
enums de tipo y moneda viven acá como TextChoices y son la única fuente de verdad
para serializers y validación de modelo.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models


class AccountType(models.TextChoices):
    """Tipos de cuenta soportados (RF-005)."""

    CASH = "cash", "Efectivo"
    DIGITAL_WALLET = "digital_wallet", "Billetera digital"
    BANK = "bank", "Banco"
    SAVINGS = "savings", "Ahorro"


class Currency(models.TextChoices):
    """Monedas soportadas (RF-005)."""

    ARS = "ARS", "Peso argentino"
    USD = "USD", "Dólar estadounidense"


class Account(models.Model):
    """Cuenta financiera de un usuario (RF-005).

    El propietario (`user`) se fija en la creación y es no editable. `is_active` es
    el hook para el archivado de RF-008 (post-MVP): los endpoints filtran solo
    cuentas activas desde el día 1.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
        editable=False,
        verbose_name="propietario",
    )
    name = models.CharField("nombre", max_length=100)
    account_type = models.CharField(
        "tipo de cuenta", max_length=20, choices=AccountType.choices
    )
    currency = models.CharField("moneda", max_length=3, choices=Currency.choices)
    initial_balance = models.DecimalField(
        "saldo inicial", max_digits=14, decimal_places=2, default=Decimal("0")
    )
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField("creada", auto_now_add=True)
    updated_at = models.DateTimeField("actualizada", auto_now=True)

    class Meta:
        verbose_name = "cuenta"
        verbose_name_plural = "cuentas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.currency})"
