import { AlertTriangle } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { ErrorState, SkeletonCards } from '@/components/common/states'
import { BalanceCards } from '@/components/dashboard/BalanceCards'
import { ExpensesChart } from '@/components/dashboard/ExpensesChart'
import { PeriodSelector } from '@/components/dashboard/PeriodSelector'
import type { Period } from '@/components/dashboard/period'
import { SummaryCards } from '@/components/dashboard/SummaryCards'
import { useDashboard } from '@/hooks/useDashboard'

function currentPeriod(): Period {
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() + 1 }
}

export function Dashboard() {
  const [period, setPeriod] = useState<Period>(currentPeriod)
  const { data, isPending, isError, refetch } = useDashboard(period.year, period.month)

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display font-bold text-2xl text-star">Dashboard</h1>
        <PeriodSelector period={period} onChange={setPeriod} />
      </header>

      {isPending && <SkeletonCards count={3} />}
      {isError && <ErrorState onRetry={() => void refetch()} />}

      {data && (
        <>
          {/* Aviso si falta TC (RF-018): los USD no se consolidan. */}
          {!data.has_exchange_rate && (
            <div className="flex items-start gap-3 rounded-lg border border-warn/30 bg-warn/10 p-4">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-warn" />
              <p className="font-body text-sm text-moon">
                Sin tipo de cambio configurado. Los balances en USD no se pueden consolidar.{' '}
                <Link to="/currency" className="font-semibold text-celeste hover:underline">
                  Configurar tipo de cambio
                </Link>
              </p>
            </div>
          )}

          <SummaryCards summary={data.summary} consolidated={data.consolidated_ars} />
          <BalanceCards balances={data.balances} />
          <ExpensesChart data={data.expenses_by_category} />
        </>
      )}
    </div>
  )
}
