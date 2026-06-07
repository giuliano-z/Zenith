import axios from 'axios'
import { useState, type FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateAccount } from '@/hooks/useAccounts'
import type { AccountType, Currency } from '@/types/account'

import { ACCOUNT_TYPE_OPTIONS } from './accountMeta'

const selectClass =
  'flex w-full rounded-lg border border-horizon bg-orbit px-3 py-2.5 text-sm font-body text-star focus:outline-none focus:border-celeste focus:ring-2 focus:ring-celeste/15 transition-all duration-150'

export function CreateAccountModal({ trigger }: { trigger: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [accountType, setAccountType] = useState<AccountType>('cash')
  const [currency, setCurrency] = useState<Currency>('ARS')
  const [initialBalance, setInitialBalance] = useState('0')
  const [error, setError] = useState<string | null>(null)

  const { mutateAsync, isPending } = useCreateAccount()

  function reset() {
    setName('')
    setAccountType('cash')
    setCurrency('ARS')
    setInitialBalance('0')
    setError(null)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await mutateAsync({
        name: name.trim(),
        account_type: accountType,
        currency,
        initial_balance: initialBalance || '0',
      })
      reset()
      setOpen(false)
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError('No se pudo crear la cuenta. Revisá los datos e intentá de nuevo.')
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
          <DialogTitle>Nueva cuenta</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="acc-name">Nombre</Label>
            <Input
              id="acc-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej: Mercado Pago"
              disabled={isPending}
              required
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="acc-type">Tipo</Label>
            <select
              id="acc-type"
              className={selectClass}
              value={accountType}
              onChange={(e) => setAccountType(e.target.value as AccountType)}
              disabled={isPending}
            >
              {ACCOUNT_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="acc-currency">Moneda</Label>
            <select
              id="acc-currency"
              className={selectClass}
              value={currency}
              onChange={(e) => setCurrency(e.target.value as Currency)}
              disabled={isPending}
            >
              <option value="ARS">ARS — Peso argentino</option>
              <option value="USD">USD — Dólar estadounidense</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="acc-balance">Balance inicial</Label>
            <Input
              id="acc-balance"
              type="number"
              step="0.01"
              value={initialBalance}
              onChange={(e) => setInitialBalance(e.target.value)}
              disabled={isPending}
            />
          </div>

          {error && (
            <p role="alert" className="font-body text-sm text-error">
              {error}
            </p>
          )}

          <Button type="submit" disabled={isPending} className="mt-2 w-full">
            {isPending ? 'Creando...' : 'Crear cuenta'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
