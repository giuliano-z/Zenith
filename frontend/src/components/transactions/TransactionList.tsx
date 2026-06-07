import { Skeleton } from '@/components/ui/skeleton'
import type { Account } from '@/types/account'
import type { Category } from '@/types/category'
import type { Transaction } from '@/types/transaction'

import { TransactionRow } from './TransactionRow'

// "2026-06-07" → "07 jun 2026" (es-AR). Se parsea como fecha local (sin TZ shift).
function formatDateHeader(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number)
  const d = new Date(year, month - 1, day)
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}

// Agrupa transacciones por fecha preservando el orden (ya vienen desc del backend).
function groupByDate(txs: Transaction[]): [string, Transaction[]][] {
  const groups = new Map<string, Transaction[]>()
  for (const tx of txs) {
    const bucket = groups.get(tx.date)
    if (bucket) bucket.push(tx)
    else groups.set(tx.date, [tx])
  }
  return [...groups.entries()]
}

export function TransactionList({
  transactions,
  accountsById,
  categoriesById,
  isLoading,
}: {
  transactions: Transaction[]
  accountsById: Map<number, Account>
  categoriesById: Map<number, Category>
  isLoading: boolean
}) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-horizon bg-nebula py-12 text-center">
        <p className="font-body text-moon">
          No hay transacciones que coincidan con los filtros.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      {groupByDate(transactions).map(([date, txs]) => (
        <section key={date}>
          <h3 className="border-t border-horizon pt-3 text-xs font-semibold uppercase text-moon">
            {formatDateHeader(date)}
          </h3>
          <div className="divide-y divide-horizon">
            {txs.map((tx) => (
              <TransactionRow
                key={tx.id}
                tx={tx}
                account={tx.account ? accountsById.get(tx.account) : undefined}
                category={tx.category ? categoriesById.get(tx.category) : undefined}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
