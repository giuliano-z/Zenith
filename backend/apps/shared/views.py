"""Endpoints HTTP del módulo SHARED (capa de presentación).

Las vistas solo orquestan: validan entrada con serializers, delegan en services.py
y devuelven la respuesta. Todas requieren token (IsAuthenticated global → 401 sin
token). Es la única excepción al aislamiento: ambos usuarios acceden a todos los
endpoints. El uso de una cuenta ajena se traduce a 403 (RS-004).
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared import services
from apps.shared.serializers import (
    SettleSerializer,
    SharedBalanceSerializer,
    SharedExpenseCreateSerializer,
    SharedExpenseSerializer,
    SharedSettlementSerializer,
)


def _forbidden():
    return Response(
        {"detail": "No tenés permiso para operar sobre esta cuenta."},
        status=status.HTTP_403_FORBIDDEN,
    )


def _not_found():
    return Response(
        {"detail": "Cuenta no encontrada."}, status=status.HTTP_404_NOT_FOUND
    )


class SharedExpenseListCreateView(APIView):
    """RF-022 (POST) y listado de historial completo (GET)."""

    def get(self, request):
        expenses = services.get_shared_expenses(request.user)
        return Response(SharedExpenseSerializer(expenses, many=True).data)

    def post(self, request):
        serializer = SharedExpenseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            expense = services.create_shared_expense(
                payer=request.user,
                account_id=data["account"],
                total_amount=data["total_amount"],
                debtor_amount=data["debtor_amount"],
                currency=data["currency"],
                date=data["date"],
                description=data["description"],
                category_id=data.get("category"),
                created_by=request.user,
            )
        except services.AccountAccessDeniedError:
            return _forbidden()
        except services.AccountNotFoundError:
            return _not_found()
        except services.SharedValidationError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            SharedExpenseSerializer(expense).data, status=status.HTTP_201_CREATED
        )


class SharedBalanceView(APIView):
    """RF-023: balance neto actual entre los dos usuarios."""

    def get(self, request):
        try:
            balance = services.get_shared_balance()
        except services.SharedValidationError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(SharedBalanceSerializer(balance).data)


class SharedSettleView(APIView):
    """RF-024: salda el balance (400 si ya está balanceado)."""

    def post(self, request):
        serializer = SettleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            settlement = services.settle_shared_balance(
                settled_by=request.user,
                from_account_id=data.get("from_account"),
                to_account_id=data.get("to_account"),
            )
        except services.AccountAccessDeniedError:
            return _forbidden()
        except services.AccountNotFoundError:
            return _not_found()
        except services.SharedValidationError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        if settlement is None:
            return Response(
                {"detail": "No hay saldo pendiente para saldar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(SharedSettlementSerializer(settlement).data)
