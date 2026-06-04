"""Contratos de entrada/salida del módulo ACCOUNTS (capa de aplicación).

Los serializers validan formato y delegan la lógica de negocio en services.py.
Los ChoiceField sobre los enums garantizan el HTTP 400 ante account_type/currency
inválidos sin que la lógica de negocio tenga que intervenir.
"""
from rest_framework import serializers

from apps.accounts import services
from apps.accounts.models import Account, AccountType, Currency


class AccountSerializer(serializers.ModelSerializer):
    """Representación pública de una cuenta (output, RF-006).

    `balance` no es un campo del modelo: se calcula en tiempo real vía el servicio
    (ADR-004). Esto mantiene el cálculo en una sola fuente de verdad.
    """

    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "account_type",
            "currency",
            "balance",
            "is_active",
            "created_at",
        )
        read_only_fields = fields

    def get_balance(self, account: Account):
        return services.get_balance(account)


class AccountCreateSerializer(serializers.Serializer):
    """Entrada de RF-005.

    `user` nunca entra por el body: lo asigna el servicio desde request.user. Los
    ChoiceField devuelven 400 ante un valor fuera del enum.
    """

    name = serializers.CharField(max_length=100)
    account_type = serializers.ChoiceField(choices=AccountType.choices)
    currency = serializers.ChoiceField(choices=Currency.choices)
    initial_balance = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False, default=0
    )
