import { AlertTriangle } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

// Grilla de skeletons para estados de carga.
export function SkeletonCards({ count = 3 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className="h-28 w-full" />
      ))}
    </div>
  )
}

// Card de error de red con botón de reintento.
export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border border-error/30 bg-error/10 p-5">
      <div className="flex items-center gap-2 text-error">
        <AlertTriangle className="h-5 w-5" />
        <p className="font-body font-semibold">No se pudieron cargar los datos.</p>
      </div>
      <p className="text-sm font-body text-moon">
        Revisá tu conexión con el servidor e intentá de nuevo.
      </p>
      <Button variant="secondary" size="sm" onClick={onRetry}>
        Reintentar
      </Button>
    </div>
  )
}
