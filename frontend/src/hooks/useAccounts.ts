import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createAccount, getAccounts } from '@/api/accounts'

const ACCOUNTS_KEY = ['accounts']

export function useAccounts() {
  return useQuery({
    queryKey: ACCOUNTS_KEY,
    queryFn: getAccounts,
  })
}

// Al crear, invalida la lista para que se refetchee con la cuenta nueva.
export function useCreateAccount() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createAccount,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ACCOUNTS_KEY })
    },
  })
}
