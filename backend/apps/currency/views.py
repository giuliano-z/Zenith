"""Endpoints HTTP del módulo CURRENCY (capa de presentación).

Las vistas solo orquestan: validan entrada con serializers, delegan en
domain/services.py y dan forma a la respuesta. Todas requieren token
(IsAuthenticated global → 401 sin token). NO hay aislamiento por usuario: el
historial de cotizaciones es global del sistema.

El provider concreto se instancia y se inyecta acá (no en los servicios), para
poder mockearlo en los tests sin patches globales.
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.currency.domain import services
from apps.currency.infrastructure.adapters.dolar_api import DolarApiProvider
from apps.currency.models import ExchangeRate
from apps.currency.serializers import (
    ExchangeRateCreateSerializer,
    ExchangeRateSerializer,
)


class CurrencyFetchView(APIView):
    """RF-017: cotización en tiempo real desde DolarAPI. NO guarda en DB.

    Provider OK → 200 con blue/oficial/tarjeta e is_fallback=false.
    Provider falla pero hay histórico en DB → 200 con is_fallback=true.
    Provider falla y DB vacía → 503.
    """

    def get(self, request):
        result = services.fetch_live_rates(DolarApiProvider())

        if "error" not in result:
            return Response(self._shape_live(result))

        fallback = result["fallback"]
        if fallback is None:
            return Response(
                {"detail": "No hay cotizaciones disponibles en este momento."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(self._shape_fallback(fallback))

    @staticmethod
    def _shape_live(rates: dict) -> dict:
        body = {
            key: {"rate": f"{value:.4f}", "source": "dolarapi"}
            for key, value in rates.items()
        }
        body["fetched_at"] = timezone.now()
        body["is_fallback"] = False
        return body

    @staticmethod
    def _shape_fallback(rate) -> dict:
        return {
            rate.rate_type: {"rate": f"{rate.rate:.4f}", "source": rate.source},
            "fetched_at": rate.created_at,
            "is_fallback": True,
        }


class ExchangeRateListCreateView(APIView):
    """RF-018 (GET) y RF-017 (POST): historial global y carga de una cotización."""

    def get(self, request):
        # Sin paginación: el volumen es bajo (una tasa por día máx).
        rates = ExchangeRate.objects.all()
        return Response(ExchangeRateSerializer(rates, many=True).data)

    def post(self, request):
        serializer = ExchangeRateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        rate = services.save_rate(
            rate=data["rate"],
            rate_type=data["rate_type"],
            effective_date=data["effective_date"],
            source=data["source"],
            user=request.user,
        )
        return Response(
            ExchangeRateSerializer(rate).data, status=status.HTTP_201_CREATED
        )


class ExchangeRateLatestView(APIView):
    """RF-017: última cotización guardada. `?rate_type=` opcional (default blue)."""

    def get(self, request):
        rate_type = request.query_params.get("rate_type", "blue")
        rate = services.get_latest_rate(rate_type)
        if rate is None:
            return Response(
                {"detail": "No hay cotizaciones guardadas."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ExchangeRateSerializer(rate).data)
