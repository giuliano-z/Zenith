import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createSharedExpense,
  getSharedBalance,
  getSharedExpenses,
  settleBalance,
} from '@/api/shared'

export function useSharedExpenses() {
  return useQuery({
    queryKey: ['shared', 'expenses'],
    queryFn: getSharedExpenses,
  })
}

// retry:false → el balance da 400 si hay <2 usuarios; queremos el error directo.
export function useSharedBalance() {
  return useQuery({
    queryKey: ['shared', 'balance'],
    queryFn: getSharedBalance,
    retry: false,
  })
}

// Un gasto/saldo compartido toca: gastos, balance, balances de cuenta y dashboard.
function useInvalidateShared() {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: ['shared', 'expenses'] })
    void queryClient.invalidateQueries({ queryKey: ['shared', 'balance'] })
    void queryClient.invalidateQueries({ queryKey: ['accounts'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  }
}

export function useCreateSharedExpense() {
  const onSuccess = useInvalidateShared()
  return useMutation({ mutationFn: createSharedExpense, onSuccess })
}

export function useSettleBalance() {
  const onSuccess = useInvalidateShared()
  return useMutation({ mutationFn: settleBalance, onSuccess })
}
