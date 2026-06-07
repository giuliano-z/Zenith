"""Lógica de negocio del módulo TRANSACTIONS (capa de dominio).

No depende de HTTP: ninguna función recibe un Request (RNF-006). Las vistas y
serializers consumen estas funciones.

Aislamiento entre usuarios (RNF-005, RS-004): toda consulta filtra por `user` y toda
cuenta usada en una transacción se valida vía `accounts.services.get_account_detail`,
que lanza `AccountAccessDeniedError` ante una cuenta ajena. La view la traduce a 403,
nunca a 404 (no se confirma la existencia de recursos de otros).
"""
from datetime import date as date_cls
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction as db_transaction
from django.db.models import Case, F, Q, Sum, When
from django.db.models import DecimalField as DjDecimal
from django.utils import timezone

from apps.accounts import services as account_services
from apps.transactions.models import Category, InstallmentPurchase, Transaction

# Reexportamos la excepción de accounts: ownership de cuenta es una sola fuente de
# verdad (RS-004). Las views de transactions atrapan este mismo símbolo.
AccountAccessDeniedError = account_services.AccountAccessDeniedError
AccountNotFoundError = account_services.AccountNotFoundError


def get_transaction_sum_for_account(account_id: int, as_of_date=None) -> Decimal:
    """ADR-004: suma neta de transacciones para el balance de una cuenta.

    income / transfer_in suman; expense / transfer_out restan. `amount` siempre es
    positivo: el signo lo decide el tipo. `as_of_date` recorta cuotas futuras
    (date > cutoff no impacta); si es None usa la fecha local de hoy.
    """
    cutoff = as_of_date or timezone.localdate()

    qs = Transaction.objects.filter(
        account_id=account_id,
        is_active=True,
        date__lte=cutoff,
    )
    result = qs.aggregate(
        net=Sum(
            Case(
                When(
                    transaction_type__in=[
                        Transaction.TransactionType.INCOME,
                        Transaction.TransactionType.TRANSFER_IN,
                    ],
                    then=F("amount"),
                ),
                default=-F("amount"),
                output_field=DjDecimal(max_digits=14, decimal_places=2),
            )
        )
    )
    return result["net"] or Decimal("0")


def _assert_account_owned(*, user, account_id: int):
    """Valida que la cuenta exista y sea del usuario; devuelve la cuenta.

    Reusa get_account_detail de accounts: lanza AccountNotFoundError (→ 404) o
    AccountAccessDeniedError (→ 403). Centraliza el chequeo de ownership (RS-004).
    """
    return account_services.get_account_detail(user=user, account_id=account_id)


def create_transaction(
    *,
    user,
    account_id: int,
    amount: Decimal,
    transaction_type: str,
    date,
    category_id: int | None = None,
    description: str = "",
) -> Transaction:
    """Crea una transacción simple income/expense (RF-009).

    Valida ownership de la cuenta antes de crear (403 si es ajena). Los tipos de
    transferencia NO entran por acá: tienen su propio servicio (create_transfer),
    que garantiza la creación del par vinculado.
    """
    _assert_account_owned(user=user, account_id=account_id)
    return Transaction.objects.create(
        user=user,
        account_id=account_id,
        category_id=category_id,
        amount=amount,
        transaction_type=transaction_type,
        date=date,
        description=description,
    )


@db_transaction.atomic
def create_transfer(
    *,
    user,
    from_account_id: int,
    to_account_id: int,
    amount: Decimal,
    date,
    description: str = "",
) -> tuple[Transaction, Transaction]:
    """Transferencia entre dos cuentas propias (RF-009).

    Crea DOS transacciones vinculadas por `transfer_pair`: TRANSFER_OUT en origen y
    TRANSFER_IN en destino. Ambas cuentas deben ser del usuario (403 si alguna es
    ajena). Atómico: o se crean las dos o ninguna.
    """
    _assert_account_owned(user=user, account_id=from_account_id)
    _assert_account_owned(user=user, account_id=to_account_id)

    out_tx = Transaction.objects.create(
        user=user,
        account_id=from_account_id,
        amount=amount,
        transaction_type=Transaction.TransactionType.TRANSFER_OUT,
        date=date,
        description=description,
    )
    in_tx = Transaction.objects.create(
        user=user,
        account_id=to_account_id,
        amount=amount,
        transaction_type=Transaction.TransactionType.TRANSFER_IN,
        date=date,
        description=description,
        transfer_pair=out_tx,
    )
    out_tx.transfer_pair = in_tx
    out_tx.save(update_fields=["transfer_pair"])
    return out_tx, in_tx


@db_transaction.atomic
def create_installment(
    *,
    user,
    account_id: int,
    total_amount: Decimal,
    installment_count: int,
    first_installment_date: date_cls,
    category_id: int | None = None,
    description: str = "",
) -> InstallmentPurchase:
    """Compra en cuotas (RF-010).

    Crea el InstallmentPurchase y genera N transacciones EXPENSE, una por cuota, con
    fechas mensuales consecutivas desde `first_installment_date`. El monto por cuota
    es total / count. El balance solo reflejará las cuotas con date <= hoy, porque
    get_transaction_sum_for_account recorta las futuras (ADR-004). Atómico.
    """
    _assert_account_owned(user=user, account_id=account_id)
    amount_per_installment = total_amount / installment_count

    purchase = InstallmentPurchase.objects.create(
        user=user,
        account_id=account_id,
        category_id=category_id,
        total_amount=total_amount,
        installment_count=installment_count,
        amount_per_installment=amount_per_installment,
        first_installment_date=first_installment_date,
        description=description,
    )

    for n in range(installment_count):
        Transaction.objects.create(
            user=user,
            account_id=account_id,
            category_id=category_id,
            amount=amount_per_installment,
            transaction_type=Transaction.TransactionType.EXPENSE,
            date=first_installment_date + relativedelta(months=n),
            description=description,
            installment_purchase=purchase,
            installment_number=n + 1,
        )
    return purchase


def list_transactions(
    *,
    user,
    account_id: int | None = None,
    category_id: int | None = None,
    transaction_type: str | None = None,
    date_from=None,
    date_to=None,
):
    """Transacciones activas del usuario con filtros opcionales (RF-011).

    SIEMPRE filtra por `user` (RNF-005): nunca devuelve movimientos de otro. Los
    demás filtros se aplican solo si vienen. Orden por fecha desc; la paginación la
    aplica la view.
    """
    qs = Transaction.objects.filter(user=user, is_active=True)
    if account_id is not None:
        qs = qs.filter(account_id=account_id)
    if category_id is not None:
        qs = qs.filter(category_id=category_id)
    if transaction_type:
        qs = qs.filter(transaction_type=transaction_type)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs.order_by("-date", "-created_at")


def list_categories(*, user, category_type: str | None = None):
    """Categorías visibles para el usuario (RF-014, RF-015).

    Incluye las del sistema (user=None, sembradas por migración) y las propias del
    usuario; nunca las privadas de otro (RNF-005). Filtra por `category_type` si
    viene. Orden por nombre. Read-only: alimenta el selector de categorías del front.
    """
    qs = Category.objects.filter(Q(user=None) | Q(user=user))
    if category_type:
        qs = qs.filter(category_type=category_type)
    return qs.order_by("name")


__all__ = [
    "AccountAccessDeniedError",
    "AccountNotFoundError",
    "get_transaction_sum_for_account",
    "create_transaction",
    "create_transfer",
    "create_installment",
    "list_transactions",
    "list_categories",
]
