"""Endpoints HTTP del módulo TRANSACTIONS (capa de presentación).

Las vistas solo orquestan: validan entrada con serializers, delegan en services.py y
devuelven la respuesta. Todas requieren token (IsAuthenticated global → 401 sin token).
El uso de una cuenta ajena se traduce a 403, nunca a 404 (RS-004). El listado SIEMPRE
filtra por request.user y se pagina de a 20 (RF-011).
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardPagination
from apps.transactions import services
from apps.transactions.serializers import (
    CategorySerializer,
    InstallmentCreateSerializer,
    TransactionCreateSerializer,
    TransactionSerializer,
    TransferCreateSerializer,
)


def _forbidden():
    """403 ante cuenta ajena (RS-004). Nueva Response por request: las de DRF son
    stateful (se renderizan una sola vez), no se pueden compartir entre llamadas."""
    return Response(
        {"detail": "No tenés permiso para operar sobre esta cuenta."},
        status=status.HTTP_403_FORBIDDEN,
    )


class CategoryListView(APIView):
    """RF-014: listado de categorías visibles para el usuario (GET).

    Read-only y sin paginar (son pocas). Filtra opcionalmente por `category_type`.
    """

    def get(self, request):
        qs = services.list_categories(
            user=request.user,
            category_type=request.query_params.get("category_type"),
        )
        return Response(CategorySerializer(qs, many=True).data)


class TransactionListCreateView(APIView):
    """RF-011 (GET, paginado con filtros) y RF-009 (POST, transacción simple)."""

    def get(self, request):
        qs = services.list_transactions(
            user=request.user,
            account_id=request.query_params.get("account_id"),
            category_id=request.query_params.get("category_id"),
            transaction_type=request.query_params.get("transaction_type"),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = TransactionSerializer(page, many=True).data
        return paginator.get_paginated_response(data)

    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            tx = services.create_transaction(
                user=request.user,
                account_id=data["account_id"],
                category_id=data.get("category_id"),
                amount=data["amount"],
                transaction_type=data["transaction_type"],
                date=data["date"],
                description=data["description"],
            )
        except services.AccountAccessDeniedError:
            return _forbidden()
        except services.AccountNotFoundError:
            return Response(
                {"detail": "Cuenta no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            TransactionSerializer(tx).data, status=status.HTTP_201_CREATED
        )


class TransferCreateView(APIView):
    """RF-009: transferencia entre cuentas propias (crea el par vinculado)."""

    def post(self, request):
        serializer = TransferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            out_tx, in_tx = services.create_transfer(
                user=request.user,
                from_account_id=data["from_account_id"],
                to_account_id=data["to_account_id"],
                amount=data["amount"],
                date=data["date"],
                description=data["description"],
            )
        except services.AccountAccessDeniedError:
            return _forbidden()
        except services.AccountNotFoundError:
            return Response(
                {"detail": "Cuenta no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "from": TransactionSerializer(out_tx).data,
                "to": TransactionSerializer(in_tx).data,
            },
            status=status.HTTP_201_CREATED,
        )


class InstallmentCreateView(APIView):
    """RF-010: compra en cuotas (genera N transacciones EXPENSE)."""

    def post(self, request):
        serializer = InstallmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            purchase = services.create_installment(
                user=request.user,
                account_id=data["account_id"],
                category_id=data.get("category_id"),
                total_amount=data["total_amount"],
                installment_count=data["installment_count"],
                first_installment_date=data["first_installment_date"],
                description=data["description"],
            )
        except services.AccountAccessDeniedError:
            return _forbidden()
        except services.AccountNotFoundError:
            return Response(
                {"detail": "Cuenta no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        transactions = purchase.transactions.order_by("date")
        return Response(
            {
                "id": purchase.id,
                "total_amount": purchase.total_amount,
                "installment_count": purchase.installment_count,
                "amount_per_installment": purchase.amount_per_installment,
                "first_installment_date": purchase.first_installment_date,
                "transactions": TransactionSerializer(transactions, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )
