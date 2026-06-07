"""Lógica de negocio del módulo SHARED (capa de dominio).

No depende de HTTP (RNF-006): ninguna función recibe un Request. Es la ÚNICA
excepción al aislamiento por usuario: ambos usuarios operan sobre los mismos
datos compartidos, por diseño (RF-022/023/024).

Ownership puntual sí se valida: la cuenta del pagador debe ser suya, y al saldar
la cuenta origen debe ser del deudor y la destino del acreedor. Para eso se
reusa accounts.services.get_account_detail (403/404) — ownership de cuenta es una
sola fuente de verdad (RS-004).
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction as db_transaction
from django.db.models import Q, Sum

from apps.accounts import services as account_services
from apps.shared.models import SharedExpense, SharedSettlement
from apps.transactions import services as transaction_services
from apps.transactions.models import Transaction

User = get_user_model()

# Reexportamos las excepciones de accounts: ownership de cuenta es una sola
# fuente de verdad (RS-004). Las views de shared atrapan estos mismos símbolos.
AccountAccessDeniedError = account_services.AccountAccessDeniedError
AccountNotFoundError = account_services.AccountNotFoundError


class SharedValidationError(Exception):
    """Dato inválido de un gasto/saldo compartido. La view la traduce a 400."""


def _get_two_active_users() -> tuple:
    """Los dos usuarios activos del sistema, ordenados por id.

    SHARED se diseñó para exactamente dos usuarios. Si hay menos de dos, no hay
    con quién compartir: lanza SharedValidationError en vez de romper con un
    IndexError. Si hubiera más de dos, toma los dos primeros por id (coherente
    con el .first()/.exclude del diseño original).
    """
    users = list(User.objects.filter(is_active=True).order_by("id")[:2])
    if len(users) < 2:
        raise SharedValidationError(
            "Se necesitan dos usuarios activos para los gastos compartidos."
        )
    return users[0], users[1]


def create_shared_expense(
    *,
    payer,
    account_id: int,
    total_amount: Decimal,
    debtor_amount: Decimal,
    currency: str,
    date,
    description: str,
    category_id: int | None = None,
    created_by,
) -> SharedExpense:
    """Registra un gasto compartido (RF-022). Atómico: gasto + transacción.

    Crea una Transaction tipo expense por el total en la cuenta del pagador (su
    balance refleja el gasto completo, ADR-004) y el SharedExpense con el monto
    que adeuda el otro usuario, fijado al momento del registro.
    """
    with db_transaction.atomic():
        # 403/404 si la cuenta no es del pagador o no existe.
        account = account_services.get_account_detail(
            user=payer, account_id=account_id
        )
        if account.currency != currency:
            raise SharedValidationError(
                "La moneda del gasto no coincide con la de la cuenta."
            )

        _, other = _participants(payer)

        transaction = transaction_services.create_transaction(
            user=payer,
            account_id=account_id,
            amount=total_amount,
            transaction_type=Transaction.TransactionType.EXPENSE,
            date=date,
            category_id=category_id,
            description=description,
        )

        return SharedExpense.objects.create(
            description=description,
            total_amount=total_amount,
            currency=currency,
            date=date,
            category_id=category_id,
            payer=payer,
            debtor=other,
            debtor_amount=debtor_amount,
            account=account,
            transaction=transaction,
            created_by=created_by,
        )


def _participants(payer):
    """Devuelve (payer, debtor): el otro usuario activo es el deudor."""
    user_a, user_b = _get_two_active_users()
    if payer.id == user_a.id:
        return user_a, user_b
    if payer.id == user_b.id:
        return user_b, user_a
    raise SharedValidationError(
        "El pagador no es uno de los usuarios de gastos compartidos."
    )


def get_shared_expenses(user):
    """Historial completo de gastos compartidos del usuario (settled + unsettled).

    Incluye los gastos donde es pagador O deudor. Orden por -date, -created_at.
    """
    return SharedExpense.objects.filter(Q(payer=user) | Q(debtor=user))


def get_shared_balance() -> dict:
    """Balance neto entre los dos usuarios sobre gastos sin saldar (RF-023).

    net = (lo que el deudor le debe a user_a) - (lo que le debe a user_b).
    Positivo → user_b le debe a user_a; negativo → al revés; cero → al día.
    El acreedor/deudor es None cuando están balanceados.

    MVP de moneda única: si hay gastos sin saldar en más de una moneda lanza
    SharedValidationError (no se pueden sumar ARS y USD).
    """
    user_a, user_b = _get_two_active_users()
    unsettled = SharedExpense.objects.filter(is_settled=False)

    currency = _single_currency(unsettled)

    a_owed = unsettled.filter(payer=user_a).aggregate(t=Sum("debtor_amount"))["t"] or Decimal("0")
    b_owed = unsettled.filter(payer=user_b).aggregate(t=Sum("debtor_amount"))["t"] or Decimal("0")
    net = a_owed - b_owed

    if net == 0:
        return {
            "net_amount": Decimal("0"),
            "creditor": None,
            "debtor": None,
            "is_balanced": True,
            "currency": currency,
        }
    creditor, debtor = (user_a, user_b) if net > 0 else (user_b, user_a)
    return {
        "net_amount": abs(net),
        "creditor": creditor,
        "debtor": debtor,
        "is_balanced": False,
        "currency": currency,
    }


def _single_currency(unsettled) -> str | None:
    """Moneda única de los gastos sin saldar, o None si no hay ninguno.

    Lanza SharedValidationError si conviven varias monedas (MVP no consolida).
    """
    # order_by("currency") explícito: sin esto, Meta.ordering (date, created_at)
    # entra en el DISTINCT y rompe la deduplicación por moneda.
    currencies = list(
        unsettled.order_by("currency").values_list("currency", flat=True).distinct()
    )
    if not currencies:
        return None
    if len(currencies) > 1:
        raise SharedValidationError(
            "Hay gastos compartidos sin saldar en distintas monedas."
        )
    return currencies[0]


def settle_shared_balance(
    *,
    settled_by,
    from_account_id: int | None = None,
    to_account_id: int | None = None,
) -> SharedSettlement | None:
    """Salda el balance compartido (RF-024). Atómico.

    Si ya está balanceado, retorna None. Marca todos los gastos sin saldar como
    saldados y crea un SharedSettlement con el snapshot del balance. Si se pasan
    ambas cuentas, registra el pago como par de transferencia (patrón RF-009):
    origen debe ser del deudor y destino del acreedor (403 si no).
    """
    with db_transaction.atomic():
        balance = get_shared_balance()
        if balance["is_balanced"]:
            return None

        creditor, debtor = balance["creditor"], balance["debtor"]
        out_tx, in_tx = _settle_transfer(
            debtor=debtor,
            creditor=creditor,
            amount=balance["net_amount"],
            from_account_id=from_account_id,
            to_account_id=to_account_id,
        )

        SharedExpense.objects.filter(is_settled=False).update(is_settled=True)

        return SharedSettlement.objects.create(
            net_amount=balance["net_amount"],
            creditor=creditor,
            debtor=debtor,
            settled_by=settled_by,
            transfer_out=out_tx,
            transfer_in=in_tx,
        )


def _settle_transfer(*, debtor, creditor, amount, from_account_id, to_account_id):
    """Crea el par de transferencia del pago, o (None, None) si no se registra.

    A diferencia de transactions.create_transfer (que es intra-usuario: ambas
    cuentas del mismo dueño), un saldo compartido cruza usuarios: el deudor paga
    desde SU cuenta hacia la del acreedor. Por eso se crea el par
    TRANSFER_OUT/TRANSFER_IN acá, validando cada cuenta contra su dueño esperado
    (403 vía AccountAccessDeniedError) y replicando el patrón de RF-009
    (transfer_pair vinculado).
    """
    if from_account_id is None or to_account_id is None:
        return None, None

    # 403/404: la cuenta origen debe ser del deudor y la destino del acreedor.
    account_services.get_account_detail(user=debtor, account_id=from_account_id)
    account_services.get_account_detail(user=creditor, account_id=to_account_id)

    today = _today()
    out_tx = Transaction.objects.create(
        user=debtor,
        account_id=from_account_id,
        amount=amount,
        transaction_type=Transaction.TransactionType.TRANSFER_OUT,
        date=today,
        description="Saldo de gastos compartidos",
    )
    in_tx = Transaction.objects.create(
        user=creditor,
        account_id=to_account_id,
        amount=amount,
        transaction_type=Transaction.TransactionType.TRANSFER_IN,
        date=today,
        description="Saldo de gastos compartidos",
        transfer_pair=out_tx,
    )
    out_tx.transfer_pair = in_tx
    out_tx.save(update_fields=["transfer_pair"])
    return out_tx, in_tx


def _today():
    from django.utils import timezone

    return timezone.localdate()


__all__ = [
    "AccountAccessDeniedError",
    "AccountNotFoundError",
    "SharedValidationError",
    "create_shared_expense",
    "get_shared_expenses",
    "get_shared_balance",
    "settle_shared_balance",
]
