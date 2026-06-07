import { usePrivacy } from '@/store/PrivacyContext'

export type Currency = 'ARS' | 'USD'

const MASK = '••••'

// Formateadores es-AR. Los montos financieros se muestran sin decimales
// (el backend maneja la precisión; la UI prioriza legibilidad).
const formatters: Record<Currency, Intl.NumberFormat> = {
  ARS: new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }),
  USD: new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }),
}

const symbols: Record<Currency, string> = {
  ARS: '$',
  USD: 'U$D',
}

/** Formatea un monto respetando el modo privacidad.
 *  En modo privado devuelve "••••"; si no, "$1.234.567" / "U$D 1.234". */
export function useMoney() {
  const { isPrivate } = usePrivacy()

  return (amount: string | number | null | undefined, currency: Currency = 'ARS'): string => {
    if (isPrivate) {
      return MASK
    }
    const value = typeof amount === 'string' ? Number(amount) : (amount ?? 0)
    if (!Number.isFinite(value)) {
      return MASK
    }
    return `${symbols[currency]} ${formatters[currency].format(value)}`.replace('  ', ' ')
  }
}
