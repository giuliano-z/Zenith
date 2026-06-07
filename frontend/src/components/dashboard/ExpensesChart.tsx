import { PieChartIcon } from 'lucide-react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

import { useMoney } from '@/hooks/useMoney'
import type { ExpenseByCategory } from '@/types/dashboard'

// Paleta AUSTRAL para series del gráfico, en el orden indicado por el spec.
// Hex acá es inevitable: recharts pinta vía prop `fill`, no por clase Tailwind.
// Mantener sincronizado con tailwind.config.js.
const SERIES_COLORS = [
  '#4AAEEE', // celeste
  '#3DAF7A', // ok
  '#E09A3D', // warn
  '#E05252', // error
  '#B8C8D8', // steel
  '#D4A837', // sol
]

interface ChartDatum {
  name: string
  value: number
  percentage: string
  currency: 'ARS' | 'USD'
}

export function ExpensesChart({ data }: { data: ExpenseByCategory[] }) {
  const money = useMoney()

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-horizon bg-nebula py-12 text-center">
        <PieChartIcon className="h-8 w-8 text-dusk" />
        <p className="font-body text-moon">Sin gastos registrados este mes.</p>
      </div>
    )
  }

  const chartData: ChartDatum[] = data.map((d) => ({
    name: d.category_name ?? 'Sin categoría',
    value: Number(d.amount),
    percentage: d.percentage,
    currency: d.currency,
  }))

  return (
    <div className="rounded-lg border border-horizon bg-nebula p-6">
      <h3 className="font-display font-semibold text-xl text-star">Gastos por categoría</h3>

      <div className="mt-4 grid gap-6 md:grid-cols-2">
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={85}
                paddingAngle={2}
                stroke="none"
              >
                {chartData.map((_, i) => (
                  <Cell key={i} fill={SERIES_COLORS[i % SERIES_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: '#12162A',
                  border: '1px solid #252B42',
                  borderRadius: '0.75rem',
                  color: '#EDF0F8',
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                }}
                formatter={(_value, _name, item) => {
                  const datum = item.payload as ChartDatum
                  return [money(datum.value, datum.currency), datum.name]
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Leyenda: nombre + porcentaje + monto */}
        <ul className="flex flex-col justify-center gap-2">
          {chartData.map((d, i) => (
            <li key={i} className="flex items-center gap-3 text-sm">
              <span
                className="h-3 w-3 shrink-0 rounded-sm"
                style={{ background: SERIES_COLORS[i % SERIES_COLORS.length] }}
              />
              <span className="flex-1 truncate font-body text-star">{d.name}</span>
              <span className="font-mono text-moon">{d.percentage}%</span>
              <span className="font-mono text-star">{money(d.value, d.currency)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
