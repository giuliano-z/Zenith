"""Endpoints HTTP del módulo ACCOUNTS (capa de presentación).

Las vistas solo orquestan: validan entrada con serializers, delegan en services.py
y devuelven la respuesta. Todas requieren token (IsAuthenticated global → 401 sin
token). El acceso a una cuenta ajena se traduce a 403, nunca a 404 (RS-004).
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts import services
from apps.accounts.serializers import AccountCreateSerializer, AccountSerializer


class AccountListCreateView(APIView):
    """RF-006 (GET) y RF-005 (POST): lista las cuentas activas del usuario y crea una."""

    def get(self, request):
        accounts = services.get_accounts(user=request.user)
        return Response(AccountSerializer(accounts, many=True).data)

    def post(self, request):
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        account = services.create_account(
            user=request.user,
            name=data["name"],
            account_type=data["account_type"],
            currency=data["currency"],
            initial_balance=data["initial_balance"],
        )
        return Response(
            AccountSerializer(account).data, status=status.HTTP_201_CREATED
        )


class AccountBalanceView(APIView):
    """CU-004: balance consolidado por moneda (solo cuentas activas del usuario)."""

    def get(self, request):
        return Response(services.get_balance_by_currency(user=request.user))


class AccountDetailView(APIView):
    """CU-003: detalle de una cuenta propia.

    Cuenta propia → 200. Cuenta ajena → 403 (NUNCA 404, RS-004). Inexistente → 404.
    """

    def get(self, request, pk):
        try:
            account = services.get_account_detail(user=request.user, account_id=pk)
        except services.AccountAccessDeniedError:
            return Response(
                {"detail": "No tenés permiso para acceder a esta cuenta."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except services.AccountNotFoundError:
            return Response(
                {"detail": "Cuenta no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AccountSerializer(account).data)
