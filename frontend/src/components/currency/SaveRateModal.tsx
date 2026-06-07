import axios from 'axios'
import { Loader2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useSaveRate } from '@/hooks/useCurrency'
import type { RateType } from '@/types/currency'

import { RATE_TYPE_OPTIONS } from './rateMeta'

const selectClass =
  'flex w-full rounded-lg border border-horizon bg-orbit px-3 py-2.5 text-sm font-body text-star focus:outline-none focus:border-celeste focus:ring-2 focus:ring-celeste/15 transition-all duration-150'

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

export function SaveRateModal({
  trigger,
  initialType = 'blue',
  initialRate = '',
}: {
  trigger: React.ReactNode
  initialType?: RateType
  initialRate?: string
}) {
  const [open, setOpen] = useState(false)
  const [rateType, setRateType] = useState<RateType>(initialType)
  const [rate, setRate] = useState(initialRate)
  const [effectiveDate, setEffectiveDate] = useState(today())
  const [error, setError] = useState<string | null>(null)

  const { mutateAsync, isPending } = useSaveRate()

  // Al abrir, (re)precargamos los valores que vienen del botón "Guardar esta tasa".
  // Se hace en el callback de apertura, no en un effect, para evitar renders en cascada.
  function handleOpenChange(next: boolean) {
    if (next) {
      setRateType(initialType)
      setRate(initialRate)
      setEffectiveDate(today())
      setError(null)
    }
    setOpen(next)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await mutateAsync({
        rate_type: rateType,
        rate,
        effective_date: effectiveDate,
        // Carga del usuario → 'manual' (sea custom o una tasa tomada de la vista).
        source: 'manual',
      })
      setOpen(false)
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError('No se pudo guardar la tasa. Revisá los datos e intentá de nuevo.')
      } else {
        setError('No se pudo conectar con el servidor.')
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Guardar tasa</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rate-type">Tipo</Label>
            <select
              id="rate-type"
              className={selectClass}
              value={rateType}
              onChange={(e) => setRateType(e.target.value as RateType)}
              disabled={isPending}
            >
              {RATE_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rate-value">Tasa (ARS por USD)</Label>
            <Input
              id="rate-value"
              type="number"
              step="0.0001"
              min="0"
              className="font-mono"
              value={rate}
              onChange={(e) => setRate(e.target.value)}
              placeholder="Ej: 1380.0000"
              disabled={isPending}
              required
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rate-date">Fecha de vigencia</Label>
            <Input
              id="rate-date"
              type="date"
              value={effectiveDate}
              onChange={(e) => setEffectiveDate(e.target.value)}
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
            {isPending ? 'Guardando...' : 'Guardar'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
