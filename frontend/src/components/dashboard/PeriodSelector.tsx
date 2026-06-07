import { ChevronLeft, ChevronRight } from 'lucide-react'

import { addMonths, type Period } from './period'

const MONTHS = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

export function PeriodSelector({
  period,
  onChange,
}: {
  period: Period
  onChange: (next: Period) => void
}) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => onChange(addMonths(period, -1))}
        aria-label="Mes anterior"
        className="rounded-lg p-2 text-moon transition-colors duration-150 hover:bg-orbit hover:text-star"
      >
        <ChevronLeft className="h-5 w-5" />
      </button>
      <span className="min-w-36 text-center font-body font-semibold text-star">
        {MONTHS[period.month - 1]} {period.year}
      </span>
      <button
        type="button"
        onClick={() => onChange(addMonths(period, 1))}
        aria-label="Mes siguiente"
        className="rounded-lg p-2 text-moon transition-colors duration-150 hover:bg-orbit hover:text-star"
      >
        <ChevronRight className="h-5 w-5" />
      </button>
    </div>
  )
}
