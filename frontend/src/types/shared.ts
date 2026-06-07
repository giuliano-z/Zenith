// Contrato del módulo SHARED (apps/shared/serializers.py).
// OJO: en SharedExpense, payer/debtor/created_by/category/account/transaction son
// IDs (números). En SharedBalance, creditor/debtor sí son objetos {id, email}.

import type { Currency } from '@/types/account'

export interface UserMini {
  id: number
  email: string
}

export interface SharedExpense {
  id: number
  description: string
  total_amount: string
  currency: Currency
  date: string // YYYY-MM-DD
  category: number | null
  payer: number
  debtor: number
  debtor_amount: string
  account: number
  transaction: number
  is_settled: boolean
  created_by: number
  created_at: string
}

export interface SharedBalance {
  net_amount: string
  creditor: UserMini | null
  debtor: UserMini | null
  is_balanced: boolean
  currency: Currency | null
}

export interface CreateSharedExpensePayload {
  account: number
  total_amount: string
  debtor_amount: string
  currency: Currency
  date: string
  description: string
  category?: number | null
}

// Ambas cuentas opcionales: o las dos o ninguna (lo valida el backend).
export interface SettlePayload {
  from_account?: number
  to_account?: number
}
