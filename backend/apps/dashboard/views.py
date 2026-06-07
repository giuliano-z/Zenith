"""Endpoint HTTP del módulo DASHBOARD (capa de presentación).

Una sola vista de solo lectura (RF-019, RF-020). Orquesta: valida los query
params, delega en domain/services.build_dashboard y serializa la salida. Token
requerido (IsAuthenticated global → 401 sin token).
"""
from datetime import date

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.domain.services import build_dashboard
from apps.dashboard.serializers import DashboardSerializer


class DashboardView(APIView):
    """RF-019/RF-020: resumen financiero del período y gastos por categoría.

    Query params opcionales `year` y `month` (default: mes actual). `month` debe
    estar en 1..12; valores no enteros o fuera de rango devuelven 400.
    """

    def get(self, request):
        today = date.today()
        try:
            year = int(request.query_params.get("year", today.year))
            month = int(request.query_params.get("month", today.month))
        except (TypeError, ValueError):
            return Response(
                {"detail": "year y month deben ser enteros."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not 1 <= month <= 12:
            return Response(
                {"detail": "month debe estar entre 1 y 12."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = build_dashboard(request.user, year, month)
        return Response(DashboardSerializer(data).data)
