import { Plus, Wallet } from 'lucide-react'

import { AccountCard } from '@/components/accounts/AccountCard'
import { CreateAccountModal } from '@/components/accounts/CreateAccountModal'
import { ErrorState } from '@/components/common/states'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useAccounts } from '@/hooks/useAccounts'

export function Accounts() {
  const { data, isPending, isError, refetch } = useAccounts()

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display font-bold text-2xl text-star">Cuentas</h1>
        <CreateAccountModal
          trigger={
            <Button>
              <Plus className="h-4 w-4" />
              Nueva cuenta
            </Button>
          }
        />
      </header>

      {isPending && (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      )}

      {isError && <ErrorState onRetry={() => void refetch()} />}

      {data && data.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-horizon bg-nebula py-16 text-center">
          <Wallet className="h-8 w-8 text-dusk" />
          <div>
            <p className="font-body text-star">Todavía no tenés cuentas.</p>
            <p className="font-body text-sm text-moon">
              Creá tu primera cuenta para empezar.
            </p>
          </div>
          <CreateAccountModal
            trigger={
              <Button>
                <Plus className="h-4 w-4" />
                Nueva cuenta
              </Button>
            }
          />
        </div>
      )}

      {data && data.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {data.map((account) => (
            <AccountCard key={account.id} account={account} />
          ))}
        </div>
      )}
    </div>
  )
}
