"""Modelos de dominio del módulo TRANSACTIONS (RF-009, RF-010, RF-014).

Tres entidades:
- `Category` (RF-014): clasifica ingresos y gastos. Las del sistema (user=None,
  is_default=True) se siembran por data migration y son comunes a todos; un usuario
  puede tener categorías propias en el futuro (post-MVP, RF-015).
- `Transaction`: el movimiento. `amount` SIEMPRE es positivo; el signo en el balance
  lo decide `transaction_type` (ADR-004), nunca el campo.
- `InstallmentPurchase` (RF-010): la compra en cuotas que agrupa N transacciones.

El balance NO se almacena: se calcula en la capa de servicio (ADR-004).
"""
from django.conf import settings
from django.db import models


class Category(models.Model):
    """Categoría de ingreso o gasto (RF-014).

    `user=None` marca una categoría del sistema (default, sembrada por migración);
    una con `user` sería propia de ese usuario. `unique_together (name, user)` permite
    que dos usuarios distintos tengan una categoría con el mismo nombre sin colisión.
    """

    class CategoryType(models.TextChoices):
        INCOME = "income", "Ingreso"
        EXPENSE = "expense", "Gasto"

    name = models.CharField("nombre", max_length=100)
    category_type = models.CharField(
        "tipo", max_length=10, choices=CategoryType.choices
    )
    color = models.CharField("color", max_length=7, blank=True, default="")
    is_default = models.BooleanField("del sistema", default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
        verbose_name="propietario",
    )
    created_at = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        unique_together = [("name", "user")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class InstallmentPurchase(models.Model):
    """Compra en cuotas (RF-010).

    Es el agrupador: registra el total y el plan de cuotas. Las N transacciones
    individuales (una por cuota) apuntan a esta instancia vía `installment_purchase`.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="installment_purchases",
        verbose_name="propietario",
    )
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="installment_purchases",
        verbose_name="cuenta",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="installment_purchases",
        null=True,
        blank=True,
        verbose_name="categoría",
    )
    total_amount = models.DecimalField(
        "monto total", max_digits=14, decimal_places=2
    )
    installment_count = models.PositiveSmallIntegerField("cantidad de cuotas")
    amount_per_installment = models.DecimalField(
        "monto por cuota", max_digits=14, decimal_places=2
    )
    first_installment_date = models.DateField("fecha primera cuota")
    description = models.CharField(
        "descripción", max_length=255, blank=True, default=""
    )
    created_at = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "compra en cuotas"
        verbose_name_plural = "compras en cuotas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.description or 'Compra'} ({self.installment_count} cuotas)"


class Transaction(models.Model):
    """Movimiento de una cuenta (RF-009, RF-010).

    `amount` es siempre positivo: el signo con el que impacta en el balance lo decide
    `transaction_type` (income/transfer_in suman; expense/transfer_out restan), tal
    como define `services.get_transaction_sum_for_account` (ADR-004).

    Una transferencia se modela como DOS transacciones (TRANSFER_OUT en origen,
    TRANSFER_IN en destino) vinculadas por `transfer_pair`. Una cuota es una EXPENSE
    ligada a su `installment_purchase` con su `installment_number`.
    """

    class TransactionType(models.TextChoices):
        INCOME = "income", "Ingreso"
        EXPENSE = "expense", "Gasto"
        TRANSFER_OUT = "transfer_out", "Transferencia saliente"
        TRANSFER_IN = "transfer_in", "Transferencia entrante"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="propietario",
    )
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="cuenta",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="transactions",
        null=True,
        blank=True,
        verbose_name="categoría",
    )
    amount = models.DecimalField("monto", max_digits=14, decimal_places=2)
    transaction_type = models.CharField(
        "tipo", max_length=15, choices=TransactionType.choices
    )
    date = models.DateField("fecha")
    description = models.CharField(
        "descripción", max_length=255, blank=True, default=""
    )
    transfer_pair = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="paired_transfer",
        null=True,
        blank=True,
        verbose_name="par de transferencia",
    )
    installment_purchase = models.ForeignKey(
        InstallmentPurchase,
        on_delete=models.SET_NULL,
        related_name="transactions",
        null=True,
        blank=True,
        verbose_name="compra en cuotas",
    )
    installment_number = models.PositiveSmallIntegerField(
        "número de cuota", null=True, blank=True
    )
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField("creada", auto_now_add=True)
    updated_at = models.DateTimeField("actualizada", auto_now=True)

    class Meta:
        verbose_name = "transacción"
        verbose_name_plural = "transacciones"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} ({self.date})"
