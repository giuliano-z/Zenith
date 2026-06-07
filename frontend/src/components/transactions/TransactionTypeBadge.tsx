import type { TransactionType } from '@/types/transaction'

import { TX_META } from './txMeta'

// Ícono + etiqueta del tipo de transacción. El círculo del ícono usa el color
// del tipo a baja opacidad (tokens AUSTRAL, sin hex).
export function TransactionTypeBadge({ type }: { type: TransactionType }) {
  const meta = TX_META[type]
  const Icon = meta.icon

  return (
    <span
      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-orbit ${meta.iconClass}`}
      title={meta.label}
    >
      <Icon className="h-4 w-4" />
    </span>
  )
}
