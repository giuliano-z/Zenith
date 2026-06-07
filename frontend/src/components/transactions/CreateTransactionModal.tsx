import axios from 'axios'
import { Loader2 } from 'lucide-react'
import { useMemo, useState, type FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCategories } from '@/hooks/useCategories'
import {
  useCreateInstallment,
  useCreateTransaction,
  useCreateTransfer,
} from '@/hooks/useTransactions'
import type { Account } from '@/types/account'

const selectClass =
  'flex w-full rounded-lg border border-horizon bg-orbit px-3 py-2.5 text-sm font-body text-star focus:outline-none focus:border-celeste focus:ring-2 focus:ring-celeste/15 transition-all duration-150'

type Mode = 'income' | 'expense' | 'transfer' | 'installment'

const MODES: { value: Mode; label: string }[] = [
  { value: 'income', label: 'Ingreso' },
  { value: 'expense', label: 'Gasto' },
  { value: 'transfer', label: 'Transferencia' },
  { value: 'installment', label: 'Cuotas' },
]

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

export function CreateTransactionModal({
  trigger,
  accounts,
}: {
  trigger: React.ReactNode
  accounts: Account[]
}) {
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<Mode>('expense')
  const [error, setError] = useState<string | null>(null)

  // Campos compartidos / por modo.
  const [accountId, setAccountId] = useState('')
  const [toAccountId, setToAccountId] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [amount, setAmount] = useState('')
  const [totalAmount, setTotalAmount] = useState('')
  const [installmentCount, setInstallmentCount] = useState('2')
  const [date, setDate] = useState(today())
  const [description, setDescription] = useState('')

  // Categorías filtradas por el tipo del modo (income/expense). Transferencia no usa.
  const categoryType = mode === 'income' ? 'income' : 'expense'
  const { data: categories = [] } = useCategories(categoryType)

  const createTransaction = useCreateTransaction()
  const createTransfer = useCreateTransfer()
  const createInstallment = useCreateInstallment()
  const isPending =
    createTransaction.isPending || createTransfer.isPending || createInstallment.isPending

  // Monto por cuota (cálculo de solo lectura para el modo cuotas).
  const amountPerInstallment = useMemo(() => {
    const total = Number(totalAmount)
    const count = Number(installmentCount)
    if (!Number.isFinite(total) || !count) return ''
    return (total / count).toFixed(2)
  }, [totalAmount, installmentCount])

  // Aviso de transferencia entre monedas distintas.
  const transferCrossCurrency = useMemo(() => {
    if (mode !== 'transfer' || !accountId || !toAccountId) return false
    const from = accounts.find((a) => a.id === Number(accountId))
    const to = accounts.find((a) => a.id === Number(toAccountId))
    return !!from && !!to && from.currency !== to.currency
  }, [mode, accountId, toAccountId, accounts])

  function reset() {
    setMode('expense')
    setAccountId('')
    setToAccountId('')
    setCategoryId('')
    setAmount('')
    setTotalAmount('')
    setInstallmentCount('2')
    setDate(today())
    setDescription('')
    setError(null)
  }

  function changeMode(next: Mode) {
    setMode(next)
    setCategoryId('') // las categorías dependen del tipo
    setError(null)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      if (mode === 'income' || mode === 'expense') {
        await createTransaction.mutateAsync({
          account_id: Number(accountId),
          category_id: categoryId ? Number(categoryId) : null,
          amount,
          transaction_type: mode,
          date,
          description: description.trim(),
        })
      } else if (mode === 'transfer') {
        await createTransfer.mutateAsync({
          from_account_id: Number(accountId),
          to_account_id: Number(toAccountId),
          amount,
          date,
          description: description.trim(),
        })
      } else {
        await createInstallment.mutateAsync({
          account_id: Number(accountId),
          category_id: categoryId ? Number(categoryId) : null,
          total_amount: totalAmount,
          installment_count: Number(installmentCount),
          first_installment_date: date,
          description: description.trim(),
        })
      }
      reset()
      setOpen(false)
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError('No se pudo registrar. Revisá los datos e intentá de nuevo.')
      } else {
        setError('No se pudo conectar con el servidor.')
      }
    }
  }

  const accountOptions = (exclude?: string) =>
    accounts
      .filter((a) => String(a.id) !== exclude)
      .map((a) => (
        <option key={a.id} value={a.id}>
          {a.name} ({a.currency})
        </option>
      ))

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
          <DialogTitle>Nueva transacción</DialogTitle>
        </DialogHeader>

        {/* Selector de modo (pills) */}
        <div className="flex flex-wrap gap-2">
          {MODES.map((m) => (
            <button
              key={m.value}
              type="button"
              onClick={() => changeMode(m.value)}
              className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-colors duration-150 ${
                mode === m.value
                  ? 'bg-celeste text-void'
                  : 'bg-orbit text-moon hover:text-star'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* --- Ingreso / Gasto --- */}
          {(mode === 'income' || mode === 'expense') && (
            <>
              <Field label="Monto" htmlFor="tx-amount">
                <Input
                  id="tx-amount"
                  type="number"
                  step="0.01"
                  min="0"
                  className="font-mono"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={isPending}
                  required
                />
              </Field>
              <Field label="Cuenta" htmlFor="tx-account">
                <select
                  id="tx-account"
                  className={selectClass}
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  disabled={isPending}
                  required
                >
                  <option value="" disabled>
                    Elegí una cuenta
                  </option>
                  {accountOptions()}
                </select>
              </Field>
              <Field label="Categoría" htmlFor="tx-category">
                <select
                  id="tx-category"
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
              </Field>
            </>
          )}

          {/* --- Transferencia --- */}
          {mode === 'transfer' && (
            <>
              <Field label="Desde" htmlFor="tx-from">
                <select
                  id="tx-from"
                  className={selectClass}
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  disabled={isPending}
                  required
                >
                  <option value="" disabled>
                    Cuenta de origen
                  </option>
                  {accountOptions(toAccountId)}
                </select>
              </Field>
              <Field label="Hacia" htmlFor="tx-to">
                <select
                  id="tx-to"
                  className={selectClass}
                  value={toAccountId}
                  onChange={(e) => setToAccountId(e.target.value)}
                  disabled={isPending}
                  required
                >
                  <option value="" disabled>
                    Cuenta de destino
                  </option>
                  {accountOptions(accountId)}
                </select>
              </Field>
              <Field label="Monto" htmlFor="tx-amount">
                <Input
                  id="tx-amount"
                  type="number"
                  step="0.01"
                  min="0"
                  className="font-mono"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={isPending}
                  required
                />
              </Field>
              {transferCrossCurrency && (
                <p className="rounded-lg border border-warn/30 bg-warn/10 px-3 py-2 text-sm text-warn">
                  Transferencia entre monedas distintas.
                </p>
              )}
            </>
          )}

          {/* --- Cuotas --- */}
          {mode === 'installment' && (
            <>
              <Field label="Descripción / comercio" htmlFor="tx-desc-inst">
                <Input
                  id="tx-desc-inst"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Ej: Heladera Frávega"
                  disabled={isPending}
                  required
                />
              </Field>
              <Field label="Monto total" htmlFor="tx-total">
                <Input
                  id="tx-total"
                  type="number"
                  step="0.01"
                  min="0"
                  className="font-mono"
                  value={totalAmount}
                  onChange={(e) => setTotalAmount(e.target.value)}
                  disabled={isPending}
                  required
                />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Field label="N° de cuotas" htmlFor="tx-count">
                  <Input
                    id="tx-count"
                    type="number"
                    min="2"
                    max="36"
                    value={installmentCount}
                    onChange={(e) => setInstallmentCount(e.target.value)}
                    disabled={isPending}
                    required
                  />
                </Field>
                <Field label="Monto por cuota" htmlFor="tx-per">
                  <Input
                    id="tx-per"
                    className="font-mono"
                    value={amountPerInstallment}
                    readOnly
                    tabIndex={-1}
                  />
                </Field>
              </div>
              <Field label="Cuenta" htmlFor="tx-account-inst">
                <select
                  id="tx-account-inst"
                  className={selectClass}
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  disabled={isPending}
                  required
                >
                  <option value="" disabled>
                    Elegí una cuenta
                  </option>
                  {accountOptions()}
                </select>
              </Field>
              <Field label="Categoría" htmlFor="tx-category-inst">
                <select
                  id="tx-category-inst"
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
              </Field>
            </>
          )}

          {/* Fecha: común a todos los modos (en cuotas, es la 1ª cuota). */}
          <Field
            label={mode === 'installment' ? 'Fecha primera cuota' : 'Fecha'}
            htmlFor="tx-date"
          >
            <Input
              id="tx-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              disabled={isPending}
              required
            />
          </Field>

          {/* Descripción: en cuotas ya está arriba como obligatoria. */}
          {mode !== 'installment' && (
            <Field label="Descripción" htmlFor="tx-desc">
              <Input
                id="tx-desc"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Opcional"
                disabled={isPending}
              />
            </Field>
          )}

          {error && (
            <p role="alert" className="font-body text-sm text-error">
              {error}
            </p>
          )}

          <Button type="submit" disabled={isPending} className="mt-2 w-full">
            {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {isPending ? 'Registrando...' : 'Registrar'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Wrapper label + campo, para no repetir el markup en cada input.
function Field({
  label,
  htmlFor,
  children,
}: {
  label: string
  htmlFor: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
    </div>
  )
}
