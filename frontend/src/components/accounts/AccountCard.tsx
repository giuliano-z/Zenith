import { useMoney } from '@/hooks/useMoney'
import type { Account } from '@/types/account'

import { ACCOUNT_TYPE_META } from './accountMeta'

export function AccountCard({ account }: { account: Account }) {
  const money = useMoney()
  const meta = ACCOUNT_TYPE_META[account.account_type]
  const Icon = meta.icon

  return (
    <div className="rounded-lg border border-horizon bg-nebula p-5 transition-all duration-150 hover:-translate-y-0.5 hover:border-celeste/40">
      <div className="flex items-start justify-between gap-3">
        <h3 className="min-w-0 truncate font-display font-semibold text-lg text-star">
          {account.name}
        </h3>
        {/* Badge de moneda */}
        <span className="shrink-0 rounded-full bg-celeste-dim px-3 py-1 text-xs font-semibold text-celeste">
          {account.currency}
        </span>
      </div>

      {/* Badge de tipo con icono */}
      <div className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-orbit px-2.5 py-1 text-xs font-body text-moon">
        <Icon className="h-3.5 w-3.5" />
        {meta.label}
      </div>

      <p className="mt-4 font-mono text-xl font-bold text-star">
        {money(account.balance, account.currency)}
      </p>
    </div>
  )
}
