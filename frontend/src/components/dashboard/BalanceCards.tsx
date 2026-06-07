import { Wallet } from 'lucide-react'

import { useMoney } from '@/hooks/useMoney'
import type { DashboardBalance } from '@/types/dashboard'

export function BalanceCards({ balances }: { balances: DashboardBalance[] }) {
  const money = useMoney()

  if (balances.length === 0) {
    return null
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {balances.map((b) => (
        <div key={b.currency} className="rounded-lg border border-horizon bg-nebula p-5">
          <div className="flex items-center gap-3">
            <span className="rounded-lg bg-celeste-dim p-2 text-celeste">
              <Wallet className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <p className="font-body text-sm text-moon">Balance {b.currency}</p>
              <p className="font-mono text-xl font-bold text-star">
                {money(b.amount, b.currency)}
              </p>
              {b.in_ars && (
                <p className="font-mono text-xs text-dusk">≈ {money(b.in_ars, 'ARS')} ARS</p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
