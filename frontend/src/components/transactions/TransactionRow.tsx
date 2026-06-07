import { useMoney } from '@/hooks/useMoney'
import type { Account } from '@/types/account'
import type { Category } from '@/types/category'
import type { Transaction } from '@/types/transaction'

import { TransactionTypeBadge } from './TransactionTypeBadge'
import { TX_META } from './txMeta'

export function TransactionRow({
  tx,
  account,
  category,
}: {
  tx: Transaction
  account?: Account
  category?: Category
}) {
  const money = useMoney()
  const meta = TX_META[tx.transaction_type]

  return (
    <div className="flex items-center gap-3 py-3">
      <TransactionTypeBadge type={tx.transaction_type} />

      <div className="min-w-0 flex-1">
        <p className="truncate font-body font-medium text-star">
          {tx.description || meta.label}
        </p>
        <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-sm">
          {category && <span className="text-moon">{category.name}</span>}
          {account && <span className="text-xs text-dusk">· {account.name}</span>}
          {tx.installment_number != null && (
            <span className="text-xs text-dusk">· cuota {tx.installment_number}</span>
          )}
        </div>
      </div>

      <p className={`shrink-0 font-mono font-bold ${meta.amountClass}`}>
        {meta.sign}
        {money(tx.amount, account?.currency ?? 'ARS')}
      </p>
    </div>
  )
}
