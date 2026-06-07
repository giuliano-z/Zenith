import { Banknote, Building2, PiggyBank, Smartphone, type LucideIcon } from 'lucide-react'

import type { AccountType } from '@/types/account'

// Metadata de presentación por tipo de cuenta (label en es-AR + icono Lucide).
export const ACCOUNT_TYPE_META: Record<AccountType, { label: string; icon: LucideIcon }> = {
  cash: { label: 'Efectivo', icon: Banknote },
  digital_wallet: { label: 'Billetera digital', icon: Smartphone },
  bank: { label: 'Cuenta bancaria', icon: Building2 },
  savings: { label: 'Caja de ahorro', icon: PiggyBank },
}

export const ACCOUNT_TYPE_OPTIONS = Object.entries(ACCOUNT_TYPE_META).map(([value, meta]) => ({
  value: value as AccountType,
  label: meta.label,
}))
