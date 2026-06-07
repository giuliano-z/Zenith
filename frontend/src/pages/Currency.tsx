import { Plus } from 'lucide-react'

import { ErrorState } from '@/components/common/states'
import { LiveRatesCard } from '@/components/currency/LiveRatesCard'
import { RateHistoryList } from '@/components/currency/RateHistoryList'
import { SaveRateModal } from '@/components/currency/SaveRateModal'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useLiveRates, useRatesHistory } from '@/hooks/useCurrency'

export function Currency() {
  const live = useLiveRates()
  const history = useRatesHistory()

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="font-display font-bold text-2xl text-star">Tipo de cambio</h1>

      {/* Sección 1 — Cotización en vivo */}
      {live.isPending && <Skeleton className="h-52 w-full" />}
      {live.isError && <ErrorState onRetry={() => void live.refetch()} />}
      {live.data && (
        <LiveRatesCard
          rates={live.data}
          onRefresh={() => void live.refetch()}
          isRefreshing={live.isFetching}
        />
      )}

      {/* Sección 2 — Guardar tasa manual */}
      <div className="flex justify-end">
        <SaveRateModal
          initialType="custom"
          trigger={
            <Button variant="secondary">
              <Plus className="h-4 w-4" />
              Ingresar tasa manual
            </Button>
          }
        />
      </div>

      {/* Sección 3 — Historial */}
      <section className="space-y-3">
        <h2 className="font-display font-semibold text-xl text-star">Historial</h2>
        {history.isError ? (
          <ErrorState onRetry={() => void history.refetch()} />
        ) : (
          <RateHistoryList rates={history.data ?? []} isLoading={history.isPending} />
        )}
      </section>
    </div>
  )
}
