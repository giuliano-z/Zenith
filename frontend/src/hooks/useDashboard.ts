import { useQuery } from '@tanstack/react-query'

import { getDashboard } from '@/api/dashboard'

// Cambiar year/month dispara un refetch automático (la queryKey los incluye).
export function useDashboard(year: number, month: number) {
  return useQuery({
    queryKey: ['dashboard', year, month],
    queryFn: () => getDashboard(year, month),
  })
}
