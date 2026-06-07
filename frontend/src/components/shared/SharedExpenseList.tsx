import { Skeleton } from '@/components/ui/skeleton'
import type { Category } from '@/types/category'
import type { SharedExpense, UserMini } from '@/types/shared'

import { SharedExpenseRow } from './SharedExpenseRow'

export function SharedExpenseList({
  expenses,
  usersById,
  categoriesById,
  isLoading,
}: {
  expenses: SharedExpense[]
  usersById: Map<number, UserMini>
  categoriesById: Map<number, Category>
  isLoading: boolean
}) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    )
  }

  if (expenses.length === 0) {
    return (
      <div className="rounded-lg border border-horizon bg-nebula py-12 text-center">
        <p className="font-body text-moon">Todavía no hay gastos compartidos.</p>
      </div>
    )
  }

  return (
    <div className="divide-y divide-horizon rounded-lg border border-horizon bg-nebula px-4">
      {expenses.map((expense) => (
        <SharedExpenseRow
          key={expense.id}
          expense={expense}
          payer={usersById.get(expense.payer)}
          category={expense.category ? categoriesById.get(expense.category) : undefined}
        />
      ))}
    </div>
  )
}
