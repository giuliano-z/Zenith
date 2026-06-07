import { cn } from '@/lib/utils'

// Skeleton AUSTRAL: superficie elevada con pulso para estados de carga.
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('animate-pulse rounded-lg bg-orbit', className)} {...props} />
}
