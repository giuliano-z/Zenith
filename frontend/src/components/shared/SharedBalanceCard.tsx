import { CheckCircle2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useMoney } from '@/hooks/useMoney'
import { useAuth } from '@/store/AuthContext'
import type { SharedBalance } from '@/types/shared'

import { SettleBalanceModal } from './SettleBalanceModal'

export function SharedBalanceCard({ balance }: { balance: SharedBalance }) {
  const money = useMoney()
  const { user } = useAuth()
  const myEmail = user?.email

  // Están al día.
  if (balance.is_balanced) {
    return (
      <div className="flex items-center justify-center gap-2 rounded-lg border border-ok/30 bg-ok/10 p-6">
        <CheckCircle2 className="h-6 w-6 text-ok" />
        <p className="font-display font-semibold text-lg text-ok">Están al día</p>
      </div>
    )
  }

  const amount = money(balance.net_amount, balance.currency ?? 'ARS')
  const iAmDebtor = myEmail != null && balance.debtor?.email === myEmail

  // Soy el deudor: le debo al acreedor.
  if (iAmDebtor) {
    return (
      <div className="rounded-lg border border-error/40 bg-error/10 p-6">
        <p className="font-body text-moon">
          Le debés a <span className="font-semibold text-star">{balance.creditor?.email}</span>
        </p>
        <p className="mt-2 font-mono text-3xl font-bold text-error">{amount}</p>
        <SettleBalanceModal
          balance={balance}
          trigger={<Button className="mt-4">Saldar deuda</Button>}
        />
      </div>
    )
  }

  // Soy el acreedor (o no puedo determinar; por defecto vista de acreedor).
  return (
    <div className="rounded-lg border border-celeste/40 bg-nebula p-6">
      <p className="font-body text-moon">
        <span className="font-semibold text-star">{balance.debtor?.email}</span> te debe
      </p>
      <p className="mt-2 font-mono text-3xl font-bold text-ok">{amount}</p>
      <SettleBalanceModal
        balance={balance}
        trigger={
          <Button variant="secondary" className="mt-4">
            Marcar como saldado
          </Button>
        }
      />
    </div>
  )
}
