import type { RateType } from '@/types/currency'

// Etiqueta de presentación por tipo de tasa (es-AR).
export const RATE_TYPE_META: Record<RateType, { label: string }> = {
  blue: { label: 'Blue' },
  oficial: { label: 'Oficial' },
  tarjeta: { label: 'Tarjeta' },
  custom: { label: 'Manual' },
}

export const RATE_TYPE_OPTIONS = (Object.keys(RATE_TYPE_META) as RateType[]).map((value) => ({
  value,
  label: RATE_TYPE_META[value].label,
}))

// "hace X minutos/horas/días" en es-AR a partir de un ISO timestamp.
export function formatRelativeTime(iso: string): string {
  const then = new Date(iso).getTime()
  if (!Number.isFinite(then)) return ''
  const diffSec = Math.round((Date.now() - then) / 1000)
  const rtf = new Intl.RelativeTimeFormat('es-AR', { numeric: 'auto' })

  if (diffSec < 60) return rtf.format(-diffSec, 'second')
  const diffMin = Math.round(diffSec / 60)
  if (diffMin < 60) return rtf.format(-diffMin, 'minute')
  const diffHr = Math.round(diffMin / 60)
  if (diffHr < 24) return rtf.format(-diffHr, 'hour')
  return rtf.format(-Math.round(diffHr / 24), 'day')
}
