// Contrato del módulo TRANSACTIONS (apps/transactions/serializers.py).
// OJO: en la respuesta, `account` y `category` son IDs (números), no objetos
// anidados. El front resuelve nombre/moneda con los listados de cuentas y categorías.

import type { Currency } from '@/types/account'

export type TransactionType = 'income' | 'expense' | 'transfer_out' | 'transfer_in'

export interface Transaction {
  id: number
  account: number
  category: number | null
  amount: string
  transaction_type: TransactionType
  date: string // YYYY-MM-DD
  description: string
  transfer_pair: number | null
  installment_purchase: number | null
  installment_number: number | null
  is_active: boolean
  created_at: string
}

// Respuesta paginada estándar de DRF (StandardPagination, RF-011).
export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Filtros de listado (RF-011). Se envían como query params; los undefined se omiten.
export interface TransactionFilters {
  account_id?: number
  category_id?: number
  transaction_type?: TransactionType
  date_from?: string
  date_to?: string
  page?: number
}

// --- Payloads de creación (RF-009, RF-010) --- //

// Transacción simple: solo income/expense (las transferencias van por su endpoint).
export interface CreateTransactionPayload {
  account_id: number
  category_id?: number | null
  amount: string
  transaction_type: 'income' | 'expense'
  date: string
  description?: string
}

export interface CreateTransferPayload {
  from_account_id: number
  to_account_id: number
  amount: string
  date: string
  description?: string
}

export interface CreateInstallmentPayload {
  account_id: number
  category_id?: number | null
  total_amount: string
  installment_count: number
  first_installment_date: string
  description?: string
}

// Re-export por conveniencia para componentes que ya importan de transaction.
export type { Currency }
