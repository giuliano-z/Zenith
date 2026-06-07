"""Modelo de dominio ExchangeRate (RF-017, RF-018).

Almacena cotizaciones USD/ARS, tanto las traídas de DolarAPI como las cargadas
a mano. A diferencia de Account, este recurso NO tiene aislamiento por usuario:
el historial de tipos de cambio es global del sistema y cualquier usuario
autenticado puede leerlo. `created_by` es auditoría (quién cargó la tasa), no
ownership: ninguna consulta filtra por él.
"""
from django.conf import settings
from django.db import models


class RateType(models.TextChoices):
    """Tipos de cotización soportados (RF-017)."""

    BLUE = "blue", "Dólar Blue"
    OFICIAL = "oficial", "Dólar Oficial"
    TARJETA = "tarjeta", "Dólar Tarjeta"
    CUSTOM = "custom", "Manual"


class Source(models.TextChoices):
    """Origen del dato: API externa o carga manual."""

    DOLARAPI = "dolarapi", "DolarAPI"
    MANUAL = "manual", "Manual"


class ExchangeRate(models.Model):
    """Cotización USD/ARS vigente a una fecha (RF-017, RF-018).

    `effective_date` es la fecha a la que aplica la tasa (no la de carga): es la
    que usa get_rate_for_date para las conversiones históricas de DASHBOARD
    (RF-018). El desempate ante varias tasas con la misma fecha es por
    created_at desc (la última cargada gana).
    """

    rate_type = models.CharField(
        "tipo", max_length=10, choices=RateType.choices, default=RateType.BLUE
    )
    rate = models.DecimalField("cotización", max_digits=12, decimal_places=4)
    effective_date = models.DateField("fecha de vigencia")
    source = models.CharField(
        "origen", max_length=10, choices=Source.choices, default=Source.DOLARAPI
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="exchange_rates",
        verbose_name="cargada por",
    )
    created_at = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "tipo de cambio"
        verbose_name_plural = "tipos de cambio"
        ordering = ["-effective_date", "-created_at"]
        indexes = [
            models.Index(fields=["-effective_date", "rate_type"]),
        ]

    def __str__(self):
        return f"{self.get_rate_type_display()} {self.rate} @ {self.effective_date}"
