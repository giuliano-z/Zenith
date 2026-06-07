// Contrato de /api/accounts/ (apps/accounts/serializers.py).

export type AccountType = 'cash' | 'digital_wallet' | 'bank' | 'savings'
export type Currency = 'ARS' | 'USD'

export interface Account {
  id: number
  name: string
  account_type: AccountType
  currency: Currency
  balance: string // calculado en tiempo real por el backend (ADR-004)
  is_active: boolean
  created_at: string
}

export interface CreateAccountPayload {
  name: string
  account_type: AccountType
  currency: Currency
  initial_balance: string
}
