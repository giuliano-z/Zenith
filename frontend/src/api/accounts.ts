import { api } from '@/api/axios'
import type { Account, CreateAccountPayload } from '@/types/account'

// RF-006: lista las cuentas activas del usuario con su balance calculado.
export async function getAccounts(): Promise<Account[]> {
  const { data } = await api.get<Account[]>('/api/accounts/')
  return data
}

// RF-005: crea una cuenta. El propietario lo asigna el backend desde el token.
export async function createAccount(payload: CreateAccountPayload): Promise<Account> {
  const { data } = await api.post<Account>('/api/accounts/', payload)
  return data
}
