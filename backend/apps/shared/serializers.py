"""Contratos de entrada/salida del módulo SHARED (capa de aplicación).

Los serializers validan formato y delegan la lógica en services.py. `payer` y
`created_by` nunca entran por el body: los pone la view desde request.user.
"""
from rest_framework import serializers

from apps.accounts.models import Currency
from apps.shared.models import SharedExpense, SharedSettlement


class UserMiniSerializer(serializers.Serializer):
    """Identificación mínima de un participante (output)."""

    id = serializers.IntegerField()
    email = serializers.EmailField()


class SharedExpenseSerializer(serializers.ModelSerializer):
    """Representación pública de un gasto compartido (output, RF-022)."""

    class Meta:
        model = SharedExpense
        fields = (
            "id",
            "description",
            "total_amount",
            "currency",
            "date",
            "category",
            "payer",
            "debtor",
            "debtor_amount",
            "account",
            "transaction",
            "is_settled",
            "created_by",
            "created_at",
        )
        read_only_fields = fields


class SharedExpenseCreateSerializer(serializers.Serializer):
    """Entrada de RF-022. `payer`/`created_by` los pone la view (request.user)."""

    account = serializers.IntegerField()
    total_amount = serializers.DecimalField(
        max_digits=12, decimal_places=4, min_value=0
    )
    debtor_amount = serializers.DecimalField(
        max_digits=12, decimal_places=4, min_value=0
    )
    currency = serializers.ChoiceField(choices=Currency.choices)
    date = serializers.DateField()
    description = serializers.CharField(max_length=255)
    category = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs["debtor_amount"] > attrs["total_amount"]:
            raise serializers.ValidationError(
                "El monto adeudado no puede superar el total."
            )
        return attrs


class SharedBalanceSerializer(serializers.Serializer):
    """Balance neto entre los dos usuarios (output, RF-023)."""

    net_amount = serializers.DecimalField(max_digits=12, decimal_places=4)
    creditor = UserMiniSerializer(allow_null=True)
    debtor = UserMiniSerializer(allow_null=True)
    is_balanced = serializers.BooleanField()
    currency = serializers.CharField(allow_null=True)


class SharedSettlementSerializer(serializers.ModelSerializer):
    """Representación de un saldo registrado (output, RF-024)."""

    class Meta:
        model = SharedSettlement
        fields = (
            "id",
            "net_amount",
            "creditor",
            "debtor",
            "settled_by",
            "settled_at",
            "transfer_out",
            "transfer_in",
        )
        read_only_fields = fields


class SettleSerializer(serializers.Serializer):
    """Entrada de RF-024. Ambas cuentas opcionales: o las dos o ninguna."""

    from_account = serializers.IntegerField(required=False, allow_null=True)
    to_account = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        has_from = attrs.get("from_account") is not None
        has_to = attrs.get("to_account") is not None
        if has_from != has_to:
            raise serializers.ValidationError(
                "Indicá ambas cuentas (origen y destino) o ninguna."
            )
        return attrs
