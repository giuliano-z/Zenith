import axios from 'axios'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useMoney } from '@/hooks/useMoney'
import { useSettleBalance } from '@/hooks/useShared'
import type { SharedBalance } from '@/types/shared'

export function SettleBalanceModal({
  trigger,
  balance,
}: {
  trigger: React.ReactNode
  balance: SharedBalance
}) {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const money = useMoney()

  const { mutateAsync, isPending } = useSettleBalance()

  async function handleConfirm() {
    setError(null)
    try {
      // Body vacío: marca el saldo sin registrar movimiento de fondos.
      await mutateAsync({})
      setOpen(false)
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError('No se pudo saldar el balance. Intentá de nuevo.')
      } else {
        setError('No se pudo conectar con el servidor.')
      }
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) setError(null)
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Saldar balance</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="rounded-lg border border-horizon bg-orbit p-4 text-center">
            <p className="font-body text-sm text-moon">Monto a saldar</p>
            <p className="mt-1 font-mono text-2xl font-bold text-star">
              {money(balance.net_amount, balance.currency ?? 'ARS')}
            </p>
          </div>

          <p className="font-body text-sm text-moon">
            Esto marca el saldo como saldado sin registrar movimiento de fondos en
            las cuentas.
          </p>

          {error && (
            <p role="alert" className="font-body text-sm text-error">
              {error}
            </p>
          )}

          <Button onClick={handleConfirm} disabled={isPending} className="w-full">
            {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {isPending ? 'Saldando...' : 'Confirmar'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
