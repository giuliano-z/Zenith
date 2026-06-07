"""Contratos de entrada/salida del módulo TRANSACTIONS (capa de aplicación).

Los serializers validan formato y delegan la lógica de negocio en services.py. Los
ChoiceField sobre los enums devuelven 400 ante valores inválidos sin que la lógica de
negocio intervenga. El `user` y el signo del balance nunca entran por el body.
"""
from rest_framework import serializers

from apps.transactions.models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    """Representación pública de una categoría (output, RF-014).

    Alimenta el selector de categorías del cliente. Read-only: las categorías del
    sistema se siembran por migración y no se crean por API en el MVP.
    """

    class Meta:
        model = Category
        fields = ("id", "name", "category_type", "color")
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    """Representación pública de una transacción (output, RF-009/RF-011)."""

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "category",
            "amount",
            "transaction_type",
            "date",
            "description",
            "transfer_pair",
            "installment_purchase",
            "installment_number",
            "is_active",
            "created_at",
        )
        read_only_fields = fields


class TransactionCreateSerializer(serializers.Serializer):
    """Entrada de RF-009 (transacción simple).

    Solo income/expense: las transferencias van por su propio endpoint, que crea el
    par vinculado. `amount` debe ser positivo (el signo lo da el tipo, no el campo).
    """

    account_id = serializers.IntegerField()
    category_id = serializers.IntegerField(required=False, allow_null=True)
    amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, min_value=0
    )
    transaction_type = serializers.ChoiceField(
        choices=[
            Transaction.TransactionType.INCOME,
            Transaction.TransactionType.EXPENSE,
        ]
    )
    date = serializers.DateField()
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )


class TransferCreateSerializer(serializers.Serializer):
    """Entrada de RF-009 (transferencia entre cuentas propias)."""

    from_account_id = serializers.IntegerField()
    to_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, min_value=0
    )
    date = serializers.DateField()
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )

    def validate(self, attrs):
        if attrs["from_account_id"] == attrs["to_account_id"]:
            raise serializers.ValidationError(
                "La cuenta origen y destino no pueden ser la misma."
            )
        return attrs


class InstallmentCreateSerializer(serializers.Serializer):
    """Entrada de RF-010 (compra en cuotas)."""

    account_id = serializers.IntegerField()
    category_id = serializers.IntegerField(required=False, allow_null=True)
    total_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, min_value=0
    )
    installment_count = serializers.IntegerField(min_value=2)
    first_installment_date = serializers.DateField()
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
