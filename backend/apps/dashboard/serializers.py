"""Contratos de salida del módulo DASHBOARD (capa de aplicación).

El dashboard es read-only y de estructura anidada. build_dashboard ya entrega
los montos formateados como string (4 decimales); estos serializers documentan
la forma de la respuesta y la validan en la salida. No hay serializer de
entrada: los query params se validan en la view.
"""
from rest_framework import serializers


class MoneyBucketSerializer(serializers.Serializer):
    """Ingresos/gastos/neto de una moneda en el período (RF-019)."""

    income = serializers.CharField()
    expenses = serializers.CharField()
    net = serializers.CharField()


class ConsolidatedArsSerializer(serializers.Serializer):
    """Totales consolidados a ARS con el TC usado (RF-019)."""

    income = serializers.CharField()
    expenses = serializers.CharField()
    net = serializers.CharField()
    rate_used = serializers.CharField()
    rate_type = serializers.CharField()
    rate_date = serializers.DateField()


class BalanceSerializer(serializers.Serializer):
    """Saldo por moneda; in_ars solo para USD cuando hay TC (RF-019)."""

    currency = serializers.CharField()
    amount = serializers.CharField()
    in_ars = serializers.CharField(allow_null=True)


class ExpenseByCategorySerializer(serializers.Serializer):
    """Gasto agregado por categoría con porcentaje (RF-020)."""

    category_id = serializers.IntegerField(allow_null=True)
    category_name = serializers.CharField(allow_null=True)
    amount = serializers.CharField()
    percentage = serializers.CharField()
    currency = serializers.CharField()


class PeriodSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    """Respuesta completa del dashboard (RF-019, RF-020)."""

    period = PeriodSerializer()
    # summary es un dict moneda → bucket; lo serializamos como mapeo.
    summary = serializers.DictField(child=MoneyBucketSerializer())
    consolidated_ars = ConsolidatedArsSerializer(allow_null=True)
    balances = BalanceSerializer(many=True)
    expenses_by_category = ExpenseByCategorySerializer(many=True)
    has_exchange_rate = serializers.BooleanField()
