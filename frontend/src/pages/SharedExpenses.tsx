import { Plus } from 'lucide-react'
import { useMemo } from 'react'

import { ErrorState } from '@/components/common/states'
import { CreateSharedExpenseModal } from '@/components/shared/CreateSharedExpenseModal'
import { SharedBalanceCard } from '@/components/shared/SharedBalanceCard'
import { SharedExpenseList } from '@/components/shared/SharedExpenseList'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useAccounts } from '@/hooks/useAccounts'
import { useCategories } from '@/hooks/useCategories'
import { useSharedBalance, useSharedExpenses } from '@/hooks/useShared'
import type { Category } from '@/types/category'
import type { UserMini } from '@/types/shared'

export function SharedExpenses() {
  const balance = useSharedBalance()
  const expenses = useSharedExpenses()
  const { data: accounts = [] } = useAccounts()
  const { data: categories = [] } = useCategories()

  // Los emails de los participantes solo vienen en el balance (creditor/debtor).
  // Con eso resolvemos el id→email de cada fila de gasto.
  const usersById = useMemo(() => {
    const map = new Map<number, UserMini>()
    if (balance.data?.creditor) map.set(balance.data.creditor.id, balance.data.creditor)
    if (balance.data?.debtor) map.set(balance.data.debtor.id, balance.data.debtor)
    return map
  }, [balance.data])

  const categoriesById = useMemo(
    () => new Map<number, Category>(categories.map((c) => [c.id, c])),
    [categories],
  )

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display font-bold text-2xl text-star">Gastos compartidos</h1>
        <CreateSharedExpenseModal
          accounts={accounts}
          trigger={
            <Button>
              <Plus className="h-4 w-4" />
              Nuevo gasto
            </Button>
          }
        />
      </header>

      {/* Balance */}
      {balance.isPending && <Skeleton className="h-32 w-full" />}
      {balance.isError && <ErrorState onRetry={() => void balance.refetch()} />}
      {balance.data && <SharedBalanceCard balance={balance.data} />}

      {/* Historial */}
      <section className="space-y-3">
        <h2 className="font-display font-semibold text-xl text-star">Historial</h2>
        {expenses.isError ? (
          <ErrorState onRetry={() => void expenses.refetch()} />
        ) : (
          <SharedExpenseList
            expenses={expenses.data ?? []}
            usersById={usersById}
            categoriesById={categoriesById}
            isLoading={expenses.isPending}
          />
        )}
      </section>
    </div>
  )
}
