import { AlertTriangle, RefreshCw } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useMoney } from '@/hooks/useMoney'
import type { LiveRateKey, LiveRates } from '@/types/currency'

import { formatRelativeTime, RATE_TYPE_META } from './rateMeta'
import { SaveRateModal } from './SaveRateModal'

const KEYS: LiveRateKey[] = ['blue', 'oficial', 'tarjeta']

export function LiveRatesCard({
  rates,
  onRefresh,
  isRefreshing,
}: {
  rates: LiveRates
  onRefresh: () => void
  isRefreshing: boolean
}) {
  const money = useMoney()

  return (
    <div className="rounded-lg border border-horizon bg-nebula p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display font-semibold text-xl text-star">Cotización en vivo</h2>
        <Button variant="ghost" size="sm" onClick={onRefresh} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      {rates.is_fallback && (
        <div className="mt-4 flex items-start gap-3 rounded-lg border border-warn/30 bg-warn/10 p-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-warn" />
          <p className="font-body text-sm text-moon">
            Mostrando última tasa guardada — dolarapi.com no disponible.
          </p>
        </div>
      )}

      <div className="mt-5 grid gap-4 sm:grid-cols-3">
        {KEYS.map((key) => {
          const live = rates[key]
          if (!live) return null
          return (
            <div key={key} className="rounded-lg border border-horizon bg-orbit p-4">
              <p className="font-body text-sm text-moon">{RATE_TYPE_META[key].label}</p>
              <p className="mt-1 font-mono text-2xl font-bold text-celeste">
                {money(live.rate, 'ARS')}
              </p>
              <SaveRateModal
                initialType={key}
                initialRate={live.rate}
                trigger={
                  <button
                    type="button"
                    className="mt-3 text-xs font-semibold text-celeste transition-colors duration-150 hover:text-celeste-bright"
                  >
                    Guardar esta tasa
                  </button>
                }
              />
            </div>
          )
        })}
      </div>

      <p className="mt-4 font-body text-xs text-dusk">
        Actualizado: {formatRelativeTime(rates.fetched_at)}
      </p>
    </div>
  )
}
