import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createInstallment,
  createTransaction,
  createTransfer,
  getTransactions,
} from '@/api/transactions'
import type { TransactionFilters } from '@/types/transaction'

const TRANSACTIONS_KEY = ['transactions']

export function useTransactions(filters: TransactionFilters) {
  return useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => getTransactions(filters),
  })
}

// Un movimiento cambia la lista, los balances de cuentas y el dashboard:
// invalidamos las tres familias de queries tras cualquier alta.
function useInvalidateAfterWrite() {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY })
    void queryClient.invalidateQueries({ queryKey: ['accounts'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  }
}

export function useCreateTransaction() {
  const onSuccess = useInvalidateAfterWrite()
  return useMutation({ mutationFn: createTransaction, onSuccess })
}

export function useCreateTransfer() {
  const onSuccess = useInvalidateAfterWrite()
  return useMutation({ mutationFn: createTransfer, onSuccess })
}

export function useCreateInstallment() {
  const onSuccess = useInvalidateAfterWrite()
  return useMutation({ mutationFn: createInstallment, onSuccess })
}
