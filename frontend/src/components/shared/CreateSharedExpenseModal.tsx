import axios from 'axios'
import { Loader2 } from 'lucide-react'
import { useMemo, useState, type FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useMoney } from '@/hooks/useMoney'
import { useCategories } from '@/hooks/useCategories'
import { useCreateSharedExpense } from '@/hooks/useShared'
import type { Account } from '@/types/account'

const selectClass =
  'flex w-full rounded-lg border border-horizon bg-orbit px-3 py-2.5 text-sm font-body text-star focus:outline-none focus:border-celeste focus:ring-2 focus:ring-celeste/15 transition-all duration-150'

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

export function CreateSharedExpenseModal({
  trigger,
  accounts,
}: {
  trigger: React.ReactNode
  accounts: Account[]
}) {
  const [open, setOpen] = useState(false)
  const [description, setDescription] = useState('')
  const [totalAmount, setTotalAmount] = useState('')
  const [debtorPct, setDebtorPct] = useState(50) // % que adeuda el otro
  const [accountId, setAccountId] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [date, setDate] = useState(today())
  const [error, setError] = useState<string | null>(null)

  const money = useMoney()
  const { data: categories = [] } = useCategories('expense')
  const { mutateAsync, isPending } = useCreateSharedExpense()

  // La moneda se deriva de la cuenta elegida (el backend exige que coincidan).
  const selectedAccount = accounts.find((a) => a.id === Number(accountId))
  const currency = selectedAccount?.currency ?? 'ARS'

  // Reparto en vivo: lo que adeuda el otro vs. lo que queda a tu cargo.
  const { debtorAmount, payerAmount } = useMemo(() => {
    const total = Number(totalAmount)
    if (!Number.isFinite(total) || total <= 0) {
      return { debtorAmount: 0, payerAmount: 0 }
    }
    const debtor = (total * debtorPct) / 100
    return { debtorAmount: debtor, payerAmount: total - debtor }
  }, [totalAmount, debtorPct])

  function reset() {
    setDescription('')
    setTotalAmount('')
    setDebtorPct(50)
    setAccountId('')
    setCategoryId('')
    setDate(today())
    setError(null)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await mutateAsync({
        account: Number(accountId),
        total_amount: totalAmount,
        debtor_amount: debtorAmount.toFixed(4),
        currency,
        date,
        description: description.trim(),
        category: categoryId ? Number(categoryId) : null,
      })
      reset()
      setOpen(false)
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError('No se pudo registrar el gasto. Revisá los datos e intentá de nuevo.')
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
        if (!next) reset()
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nuevo gasto compartido</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="se-desc">Descripción</Label>
            <Input
              id="se-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ej: Supermercado"
              disabled={isPending}
              required
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="se-total">Monto total</Label>
            <Input
              id="se-total"
              type="number"
              step="0.01"
              min="0"
              className="font-mono"
              value={totalAmount}
              onChange={(e) => setTotalAmount(e.target.value)}
              disabled={isPending}
              required
            />
          </div>

          {/* División por porcentaje → calcula debtor_amount */}
          <div className="flex flex-col gap-2">
            <Label htmlFor="se-split">División — el otro paga {debtorPct}%</Label>
            <input
              id="se-split"
              type="range"
              min="0"
              max="100"
              step="5"
              value={debtorPct}
              onChange={(e) => setDebtorPct(Number(e.target.value))}
              disabled={isPending}
              className="w-full accent-celeste"
            />
            <div className="flex justify-between font-mono text-sm">
              <span className="text-moon">
                Vos pagás: <span className="text-star">{money(payerAmount, currency)}</span>
              </span>
              <span className="text-moon">
                Te deben: <span className="text-warn">{money(debtorAmount, currency)}</span>
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="se-account">Cuenta (la pagás vos)</Label>
            <select
              id="se-account"
              className={selectClass}
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              disabled={isPending}
              required
            >
              <option value="" disabled>
                Elegí una cuenta
              </option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.currency})
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="se-category">Categoría</Label>
            <select
              id="se-category"
              className={selectClass}
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              disabled={isPending}
            >
              <option value="">Sin categoría</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="se-date">Fecha</Label>
            <Input
              id="se-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              disabled={isPending}
              required
            />
          </div>

          {error && (
            <p role="alert" className="font-body text-sm text-error">
              {error}
            </p>
          )}

          <Button type="submit" disabled={isPending} className="mt-2 w-full">
            {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {isPending ? 'Registrando...' : 'Registrar gasto'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
