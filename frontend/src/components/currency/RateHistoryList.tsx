import { Skeleton } from '@/components/ui/skeleton'
import { useMoney } from '@/hooks/useMoney'
import type { ExchangeRate } from '@/types/currency'

import { RATE_TYPE_META } from './rateMeta'

// "2026-06-07" → "07 jun 2026" (es-AR, fecha local sin TZ shift).
function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function RateHistoryList({
  rates,
  isLoading,
}: {
  rates: ExchangeRate[]
  isLoading: boolean
}) {
  const money = useMoney()

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (rates.length === 0) {
    return (
      <div className="rounded-lg border border-horizon bg-nebula py-10 text-center">
        <p className="font-body text-moon">No hay tasas guardadas todavía.</p>
      </div>
    )
  }

  return (
    <div className="divide-y divide-horizon rounded-lg border border-horizon bg-nebula">
      {rates.map((rate) => (
        <div key={rate.id} className="flex items-center gap-3 px-4 py-3">
          <span className="w-28 shrink-0 font-body text-sm text-moon">
            {formatDate(rate.effective_date)}
          </span>
          <span className="shrink-0 rounded-full bg-celeste-dim px-2.5 py-0.5 text-xs font-semibold text-celeste">
            {RATE_TYPE_META[rate.rate_type].label}
          </span>
          <span className="flex-1 text-right font-mono font-bold text-star">
            {money(rate.rate, 'ARS')}
          </span>
          <span className="w-20 shrink-0 text-right font-body text-xs text-dusk">
            {rate.source}
          </span>
        </div>
      ))}
    </div>
  )
}
