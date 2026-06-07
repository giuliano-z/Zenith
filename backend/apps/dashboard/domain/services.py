"""Lógica de negocio del módulo DASHBOARD (capa de dominio).

DASHBOARD no tiene modelo propio: es agregación pura sobre datos de ACCOUNTS,
TRANSACTIONS y CURRENCY (RF-019, RF-020). No depende de HTTP (RNF-006): ninguna
función recibe un Request.

Aislamiento entre usuarios (RNF-005): toda agregación parte de las cuentas
activas del usuario (get_accounts filtra por user) y filtra las transacciones a
ese conjunto, así nunca se mezclan datos de otros usuarios.

Reglas del período:
- El summary considera solo income/expense; los transfers son movimientos
  internos y no cuentan como ingreso ni gasto.
- Solo transacciones is_active=True (consistente con el balance, ADR-004).
- Las cuotas (RF-010) tienen date = vencimiento de cada cuota, así que el filtro
  por año/mes ya incluye únicamente las que caen dentro del período.
"""
from decimal import Decimal

from apps.accounts.services import get_accounts, get_balance
from apps.currency.domain.services import get_latest_rate
from apps.transactions.models import Transaction
from apps.transactions.services import get_transaction_sum_for_account

# Cuantización monetaria a 4 decimales para la salida (coincide con CURRENCY).
_Q = Decimal("0.0001")
_INCOME = Transaction.TransactionType.INCOME
_EXPENSE = Transaction.TransactionType.EXPENSE


def _money(value: Decimal) -> str:
    """Formatea un Decimal a string con 4 decimales para la respuesta."""
    return f"{(value or Decimal('0')).quantize(_Q)}"


def _period_transactions(user, year: int, month: int):
    """Transacciones activas del usuario en el período (cualquier tipo)."""
    return Transaction.objects.filter(
        account__in=get_accounts(user=user),
        is_active=True,
        date__year=year,
        date__month=month,
    )


def get_period_summary(user, year: int, month: int) -> dict:
    """Ingresos y gastos del período agrupados por moneda (RF-019).

    Excluye transfers. Devuelve {moneda: {income, expenses, net}} con Decimals;
    vacío si no hay income/expense en el período. El formateo a string lo hace
    build_dashboard.
    """
    from django.db.models import Sum

    rows = (
        _period_transactions(user, year, month)
        .filter(transaction_type__in=[_INCOME, _EXPENSE])
        .values("account__currency", "transaction_type")
        .annotate(total=Sum("amount"))
    )

    summary: dict[str, dict[str, Decimal]] = {}
    for row in rows:
        bucket = summary.setdefault(
            row["account__currency"],
            {"income": Decimal("0"), "expenses": Decimal("0")},
        )
        key = "income" if row["transaction_type"] == _INCOME else "expenses"
        bucket[key] += row["total"]

    for bucket in summary.values():
        bucket["net"] = bucket["income"] - bucket["expenses"]
    return summary


def get_account_balances(user) -> list[dict]:
    """Balance actual por moneda de las cuentas activas del usuario (RF-019).

    Reusa accounts.get_balance inyectándole la suma de transacciones
    (ADR-004), igual que get_balance_by_currency. `in_ars` lo completa
    build_dashboard según haya o no TC.
    """
    totals: dict[str, Decimal] = {}
    for account in get_accounts(user=user):
        balance = get_balance(account, get_transaction_sum_for_account(account.id))
        totals[account.currency] = totals.get(account.currency, Decimal("0")) + balance
    return [{"currency": currency, "amount": amount} for currency, amount in totals.items()]


def get_expenses_by_category(user, year: int, month: int) -> list[dict]:
    """Gastos del período por categoría con porcentaje (RF-020).

    El porcentaje es relativo al total de gastos de la MISMA moneda (ARS y USD
    se muestran en moneda nativa, sin convertir). Orden por monto desc.
    """
    from django.db.models import Sum

    rows = (
        _period_transactions(user, year, month)
        .filter(transaction_type=_EXPENSE)
        .values("category_id", "category__name", "account__currency")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    totals_por_moneda: dict[str, Decimal] = {}
    for row in rows:
        currency = row["account__currency"]
        totals_por_moneda[currency] = totals_por_moneda.get(currency, Decimal("0")) + row["total"]

    result = []
    for row in rows:
        amount = row["total"]
        if amount == 0:
            continue
        total = totals_por_moneda[row["account__currency"]]
        percentage = (amount / total * Decimal("100")).quantize(Decimal("0.01"))
        result.append(
            {
                "category_id": row["category_id"],
                "category_name": row["category__name"],
                "amount": amount,
                "percentage": percentage,
                "currency": row["account__currency"],
            }
        )
    return result


def get_consolidated_ars(summary: dict, balances: list[dict]) -> dict | None:
    """Consolida summary y balances a ARS con el TC blue más reciente (RF-019).

    Retorna None si no hay ningún TC configurado. Convierte ARS_nativo +
    USD * rate para income, expenses y net.
    """
    rate = get_latest_rate(rate_type="blue")
    if rate is None:
        return None

    ars = summary.get("ARS", {})
    usd = summary.get("USD", {})
    factor = rate.rate

    def consolidate(key: str) -> Decimal:
        return ars.get(key, Decimal("0")) + usd.get(key, Decimal("0")) * factor

    return {
        "income": consolidate("income"),
        "expenses": consolidate("expenses"),
        "net": consolidate("net"),
        "rate_used": factor,
        "rate_type": rate.rate_type,
        "rate_date": rate.effective_date,
    }


def build_dashboard(user, year: int, month: int) -> dict:
    """Arma la respuesta completa del dashboard (RF-019, RF-020).

    Única función que llama la view. Inyecta in_ars en cada balance (USD→ARS si
    hay TC; null para ARS o sin TC) y expone has_exchange_rate.
    """
    summary = get_period_summary(user, year, month)
    balances = get_account_balances(user)
    consolidated = get_consolidated_ars(summary, balances)
    expenses = get_expenses_by_category(user, year, month)

    rate = consolidated["rate_used"] if consolidated else None
    return {
        "period": {"year": year, "month": month},
        "summary": {
            currency: {k: _money(v) for k, v in bucket.items()}
            for currency, bucket in summary.items()
        },
        "consolidated_ars": _format_consolidated(consolidated),
        "balances": [_format_balance(b, rate) for b in balances],
        "expenses_by_category": [_format_expense(e) for e in expenses],
        "has_exchange_rate": consolidated is not None,
    }


def _format_consolidated(consolidated: dict | None) -> dict | None:
    """Formatea el bloque consolidado a strings (o lo deja en None)."""
    if consolidated is None:
        return None
    return {
        "income": _money(consolidated["income"]),
        "expenses": _money(consolidated["expenses"]),
        "net": _money(consolidated["net"]),
        "rate_used": _money(consolidated["rate_used"]),
        "rate_type": consolidated["rate_type"],
        "rate_date": consolidated["rate_date"],
    }


def _format_balance(balance: dict, rate: Decimal | None) -> dict:
    """Formatea un balance; calcula in_ars solo para USD cuando hay TC."""
    in_ars = None
    if balance["currency"] == "USD" and rate is not None:
        in_ars = _money(balance["amount"] * rate)
    return {
        "currency": balance["currency"],
        "amount": _money(balance["amount"]),
        "in_ars": in_ars,
    }


def _format_expense(expense: dict) -> dict:
    """Formatea una fila de gasto por categoría a strings."""
    return {
        "category_id": expense["category_id"],
        "category_name": expense["category_name"],
        "amount": _money(expense["amount"]),
        "percentage": f"{expense['percentage']}",
        "currency": expense["currency"],
    }


__all__ = [
    "get_period_summary",
    "get_account_balances",
    "get_consolidated_ars",
    "get_expenses_by_category",
    "build_dashboard",
]
