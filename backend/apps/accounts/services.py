"""Lógica de negocio del módulo ACCOUNTS (capa de dominio).

No depende de HTTP: ninguna función recibe un Request. Es testeable en aislamiento
(RNF-006). Las vistas y serializers consumen estas funciones.

Aislamiento entre usuarios (RNF-005, RS-004): toda consulta filtra por `user`.
El acceso a un recurso ajeno se distingue de uno inexistente con dos excepciones
separadas, para que la view responda 403 (nunca 404) ante una cuenta de otro.
"""
from decimal import Decimal

from apps.accounts.models import Account, Currency


class AccountNotFoundError(Exception):
    """La cuenta no existe para nadie. La view la traduce a 404."""


class AccountAccessDeniedError(Exception):
    """La cuenta existe pero es de otro usuario (RS-004).

    La view la traduce a 403, NUNCA a 404: un 404 confirmaría la existencia del
    recurso y permitiría enumerar cuentas ajenas.
    """


def create_account(
    *,
    user,
    name: str,
    account_type: str,
    currency: str,
    initial_balance: Decimal = Decimal("0"),
) -> Account:
    """Crea una cuenta para el usuario dado (RF-005).

    El propietario se asigna acá y no es editable después. La validación de los
    enums (account_type, currency) la garantizan los ChoiceField del serializer
    aguas arriba; este servicio confía en datos ya validados.
    """
    return Account.objects.create(
        user=user,
        name=name,
        account_type=account_type,
        currency=currency,
        initial_balance=initial_balance,
    )


def get_accounts(*, user):
    """Cuentas ACTIVAS del usuario, ordenadas por fecha de creación desc (RF-006).

    Filtra is_active=True desde el día 1 aunque el archivado sea post-MVP (RF-008):
    una cuenta archivada no debe aparecer en el listado.
    """
    return Account.objects.filter(user=user, is_active=True)


def get_account_detail(*, user, account_id: int) -> Account:
    """Detalle de una cuenta del usuario (CU-003).

    Lanza AccountAccessDeniedError si la cuenta existe pero pertenece a otro usuario
    (→ 403), y AccountNotFoundError si no existe para nadie (→ 404). El orden importa:
    primero verificamos existencia global, luego propiedad, para no filtrar por la
    diferencia entre "no existe" y "no es tuya".
    """
    account = Account.objects.filter(pk=account_id).first()
    if account is None:
        raise AccountNotFoundError(account_id)
    if account.user_id != user.id:
        raise AccountAccessDeniedError(account_id)
    return account


def get_balance(account: Account, transaction_sum: Decimal = Decimal("0")) -> Decimal:
    """Balance de una cuenta en tiempo real (ADR-004).

    balance = initial_balance + Σ(transacciones de la cuenta)

    El módulo TRANSACTIONS aún no existe, así que `transaction_sum` tiene default
    Decimal("0"). Cuando llegue F4, el único cambio es que el CALLER pase la suma
    real de transacciones; esta firma y las views no se tocan.
    """
    return account.initial_balance + transaction_sum


def get_balance_by_currency(*, user) -> dict[str, Decimal]:
    """Balance consolidado por moneda del usuario (CU-004).

    Solo cuentas activas, solo del usuario autenticado. Devuelve un dict por moneda
    soportada con la suma de balances de sus cuentas. Las monedas sin cuentas activas
    no aparecen en el resultado.
    """
    # ADR-004: import local para evitar el ciclo accounts ↔ transactions.
    from apps.transactions.services import get_transaction_sum_for_account

    totals: dict[str, Decimal] = {}
    for account in get_accounts(user=user):
        balance = get_balance(account, get_transaction_sum_for_account(account.id))
        totals[account.currency] = totals.get(account.currency, Decimal("0")) + balance
    return totals


__all__ = [
    "AccountNotFoundError",
    "AccountAccessDeniedError",
    "Currency",
    "create_account",
    "get_accounts",
    "get_account_detail",
    "get_balance",
    "get_balance_by_currency",
]
