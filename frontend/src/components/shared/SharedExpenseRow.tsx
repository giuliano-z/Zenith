import { useMoney } from '@/hooks/useMoney'
import type { Category } from '@/types/category'
import type { SharedExpense, UserMini } from '@/types/shared'

// "2026-06-07" → "07 jun 2026" (es-AR, fecha local).
function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function SharedExpenseRow({
  expense,
  payer,
  category,
}: {
  expense: SharedExpense
  payer?: UserMini
  category?: Category
}) {
  const money = useMoney()

  return (
    <div
      className={`flex items-center gap-3 py-3 ${expense.is_settled ? 'opacity-50' : ''}`}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="truncate font-body font-medium text-star">{expense.description}</p>
          {expense.is_settled && (
            <span className="shrink-0 rounded-full bg-orbit px-2 py-0.5 text-xs font-semibold text-moon">
              Saldado
            </span>
          )}
        </div>
        <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-sm">
          {payer && <span className="text-moon">Pagó {payer.email}</span>}
          {category && <span className="text-xs text-dusk">· {category.name}</span>}
          <span className="text-xs text-dusk">· {formatDate(expense.date)}</span>
        </div>
      </div>

      <div className="shrink-0 text-right">
        <p className="font-mono font-bold text-star">
          {money(expense.total_amount, expense.currency)}
        </p>
        <p className="font-mono text-xs text-warn">
          → debe {money(expense.debtor_amount, expense.currency)}
        </p>
      </div>
    </div>
  )
}
