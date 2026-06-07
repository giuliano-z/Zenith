import { ArrowDown, ArrowUp, TrendingDown, TrendingUp, type LucideIcon } from 'lucide-react'

import { useMoney } from '@/hooks/useMoney'
import { cn } from '@/lib/utils'
import type { ConsolidatedArs, MoneyBucket } from '@/types/dashboard'

type Kind = 'income' | 'expenses' | 'net'

const CONFIG: Record<Kind, { label: string; color: string; icon: LucideIcon }> = {
  income: { label: 'Ingresos', color: 'text-ok', icon: ArrowUp },
  expenses: { label: 'Gastos', color: 'text-error', icon: ArrowDown },
  net: { label: 'Neto', color: 'text-celeste', icon: TrendingUp },
}

interface Row {
  currency: 'ARS' | 'USD'
  value: string
}

function SummaryCard({ kind, rows }: { kind: Kind; rows: Row[] }) {
  const money = useMoney()
  const { label, color } = CONFIG[kind]
  // El ícono de "Neto" cambia según el signo del valor principal (primera fila).
  let Icon = CONFIG[kind].icon
  if (kind === 'net' && rows[0] && Number(rows[0].value) < 0) {
    Icon = TrendingDown
  }

  return (
    <div className="rounded-lg border border-horizon bg-nebula p-5">
      <div className="flex items-center justify-between">
        <span className="font-body text-sm text-moon">{label}</span>
        <Icon className={cn('h-4 w-4', color)} />
      </div>
      {rows.map((row, i) => (
        <p
          key={row.currency}
          className={cn(
            'font-mono font-bold',
            color,
            i === 0 ? 'mt-2 text-2xl' : 'mt-0.5 text-sm opacity-70'
          )}
        >
          {money(row.value, row.currency)}
          {row.currency === 'USD' && <span className="ml-1 text-xs">USD</span>}
        </p>
      ))}
    </div>
  )
}

export function SummaryCards({
  summary,
  consolidated,
}: {
  summary: Partial<Record<'ARS' | 'USD', MoneyBucket>>
  consolidated: ConsolidatedArs | null
}) {
  const money = useMoney()
  // Filas por tipo: ARS primero (principal), USD debajo si existe.
  const rowsFor = (kind: Kind): Row[] => {
    const out: Row[] = []
    if (summary.ARS) out.push({ currency: 'ARS', value: summary.ARS[kind] })
    if (summary.USD) out.push({ currency: 'USD', value: summary.USD[kind] })
    // Si no hubo movimientos en ninguna moneda, mostrar 0 en ARS.
    if (out.length === 0) out.push({ currency: 'ARS', value: '0' })
    return out
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-3">
        <SummaryCard kind="income" rows={rowsFor('income')} />
        <SummaryCard kind="expenses" rows={rowsFor('expenses')} />
        <SummaryCard kind="net" rows={rowsFor('net')} />
      </div>

      {consolidated && (
        <div className="rounded-lg border border-horizon/70 bg-orbit p-5">
          <p className="font-body text-sm text-moon">
            Consolidado en ARS{' '}
            <span className="font-mono text-dusk">
              (TC {consolidated.rate_type}: {money(consolidated.rate_used, 'ARS')})
            </span>
          </p>
          <div className="mt-3 grid gap-4 sm:grid-cols-3">
            <div>
              <p className="font-body text-xs text-dusk">Ingresos</p>
              <p className="font-mono font-bold text-ok">{money(consolidated.income, 'ARS')}</p>
            </div>
            <div>
              <p className="font-body text-xs text-dusk">Gastos</p>
              <p className="font-mono font-bold text-error">{money(consolidated.expenses, 'ARS')}</p>
            </div>
            <div>
              <p className="font-body text-xs text-dusk">Neto</p>
              <p className="font-mono font-bold text-celeste">{money(consolidated.net, 'ARS')}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
