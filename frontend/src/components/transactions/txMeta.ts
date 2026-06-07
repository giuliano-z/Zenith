import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp, type LucideIcon } from 'lucide-react'

import type { TransactionType } from '@/types/transaction'

// Metadata de presentación por tipo de transacción.
// `sign` se antepone al monto; `amountClass` colorea el monto.
// (Constante fuera del .tsx para no romper el fast-refresh de react.)
interface TxMeta {
  label: string
  icon: LucideIcon
  iconClass: string
  amountClass: string
  sign: string
}

export const TX_META: Record<TransactionType, TxMeta> = {
  income: {
    label: 'Ingreso',
    icon: ArrowDown,
    iconClass: 'text-ok',
    amountClass: 'text-ok',
    sign: '+',
  },
  expense: {
    label: 'Gasto',
    icon: ArrowUp,
    iconClass: 'text-error',
    amountClass: 'text-error',
    sign: '-',
  },
  transfer_out: {
    label: 'Transferencia enviada',
    icon: ArrowRight,
    iconClass: 'text-moon',
    amountClass: 'text-moon',
    sign: '-',
  },
  transfer_in: {
    label: 'Transferencia recibida',
    icon: ArrowLeft,
    iconClass: 'text-moon',
    amountClass: 'text-moon',
    sign: '+',
  },
}
