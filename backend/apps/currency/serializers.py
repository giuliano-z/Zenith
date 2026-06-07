"""Contratos de entrada/salida del módulo CURRENCY (capa de aplicación).

Los serializers validan formato y delegan la lógica en domain/services.py. Los
ChoiceField sobre los enums garantizan el 400 ante rate_type/source inválidos.
"""
from rest_framework import serializers

from apps.currency.models import ExchangeRate, RateType, Source


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Representación pública de una cotización (output, RF-017/RF-018)."""

    class Meta:
        model = ExchangeRate
        fields = (
            "id",
            "rate_type",
            "rate",
            "effective_date",
            "source",
            "created_at",
        )
        read_only_fields = fields


class ExchangeRateCreateSerializer(serializers.Serializer):
    """Entrada de RF-017 (POST /rates/).

    `created_by` nunca entra por el body: lo asigna el servicio desde
    request.user (auditoría). `source` se infiere: default 'dolarapi' si la tasa
    vino de /fetch/, el frontend manda 'manual' en el ingreso a mano.
    """

    rate_type = serializers.ChoiceField(choices=RateType.choices)
    rate = serializers.DecimalField(max_digits=12, decimal_places=4)
    effective_date = serializers.DateField()
    source = serializers.ChoiceField(
        choices=Source.choices, required=False, default=Source.DOLARAPI
    )
