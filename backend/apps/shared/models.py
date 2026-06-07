"""Modelos de dominio del módulo SHARED (RF-022, RF-023, RF-024).

ÚNICA excepción al aislamiento estricto por usuario (RNF-005): un gasto
compartido pertenece a DOS usuarios (payer y debtor) y ambos lo ven. Los
participantes se guardan explícitos, no se derivan en runtime.

Dos entidades:
- `SharedExpense`: el gasto compartido. Crea una Transaction (expense) en la
  cuenta del pagador, así su balance refleja el gasto total (ADR-004). El monto
  que adeuda el debtor (`debtor_amount`) se fija al registrar y no cambia.
- `SharedSettlement`: el snapshot del balance al saldar (RF-024). El pago
  opcional se modela como un par de transferencia (patrón RF-009).
"""
from django.conf import settings
from django.db import models

from apps.accounts.models import Currency


class SharedExpense(models.Model):
    """Gasto compartido entre dos usuarios (RF-022)."""

    # Evento
    description = models.CharField("descripción", max_length=255)
    total_amount = models.DecimalField("monto total", max_digits=12, decimal_places=4)
    currency = models.CharField("moneda", max_length=3, choices=Currency.choices)
    date = models.DateField("fecha")
    category = models.ForeignKey(
        "transactions.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shared_expenses",
        verbose_name="categoría",
    )

    # Participantes (explícitos — no se derivan en runtime)
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="shared_expenses_as_payer",
        verbose_name="pagador",
    )
    debtor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="shared_expenses_as_debtor",
        verbose_name="deudor",
    )
    debtor_amount = models.DecimalField(
        "monto adeudado", max_digits=12, decimal_places=4
    )

    # Cuenta y transacción del pagador
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="shared_expenses",
        verbose_name="cuenta",
    )
    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="shared_expense",
        verbose_name="transacción",
    )

    # Estado
    is_settled = models.BooleanField("saldado", default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="shared_expenses_created",
        verbose_name="registrado por",
    )
    created_at = models.DateTimeField("creado", auto_now_add=True)

    class Meta:
        verbose_name = "gasto compartido"
        verbose_name_plural = "gastos compartidos"
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["is_settled", "-date"])]

    def __str__(self):
        return f"{self.description} ({self.total_amount} {self.currency})"


class SharedSettlement(models.Model):
    """Snapshot del balance compartido al momento de saldarlo (RF-024)."""

    net_amount = models.DecimalField("monto neto", max_digits=12, decimal_places=4)
    creditor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="settlements_as_creditor",
        verbose_name="acreedor",
    )
    debtor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="settlements_as_debtor",
        verbose_name="deudor",
    )
    settled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="settlements_initiated",
        verbose_name="saldado por",
    )
    settled_at = models.DateTimeField("saldado", auto_now_add=True)

    # Pago opcional — par de transferencia idéntico al patrón de RF-009.
    transfer_out = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="settlement_as_out",
        verbose_name="transferencia saliente",
    )
    transfer_in = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="settlement_as_in",
        verbose_name="transferencia entrante",
    )

    class Meta:
        verbose_name = "saldo de gastos compartidos"
        verbose_name_plural = "saldos de gastos compartidos"
        ordering = ["-settled_at"]

    def __str__(self):
        return f"Saldo {self.net_amount} ({self.settled_at:%Y-%m-%d})"
