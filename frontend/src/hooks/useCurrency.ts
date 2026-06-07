import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchLiveRates, getRatesHistory, saveRate } from '@/api/currency'

// retry:false → si la API externa cae y no hay histórico (503), el error se
// muestra de inmediato sin reintentos que demoren el fallback.
export function useLiveRates() {
  return useQuery({
    queryKey: ['currency', 'live'],
    queryFn: fetchLiveRates,
    retry: false,
  })
}

export function useRatesHistory() {
  return useQuery({
    queryKey: ['currency', 'rates'],
    queryFn: getRatesHistory,
  })
}

// Guardar una tasa afecta el historial y el dashboard (consolida USD): invalida ambos.
export function useSaveRate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: saveRate,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['currency', 'rates'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
