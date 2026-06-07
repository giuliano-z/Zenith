// Contrato de GET /api/dashboard/ (apps/dashboard/serializers.py).
// Todos los montos llegan como string con 4 decimales.

export interface MoneyBucket {
  income: string
  expenses: string
  net: string
}

export interface ConsolidatedArs {
  income: string
  expenses: string
  net: string
  rate_used: string
  rate_type: string
  rate_date: string
}

export interface DashboardBalance {
  currency: 'ARS' | 'USD'
  amount: string
  in_ars: string | null
}

export interface ExpenseByCategory {
  category_id: number | null
  category_name: string | null
  amount: string
  percentage: string
  currency: 'ARS' | 'USD'
}

export interface Dashboard {
  period: { year: number; month: number }
  // summary es un mapeo moneda → bucket (puede traer ARS, USD o ambas).
  summary: Partial<Record<'ARS' | 'USD', MoneyBucket>>
  consolidated_ars: ConsolidatedArs | null
  balances: DashboardBalance[]
  expenses_by_category: ExpenseByCategory[]
  has_exchange_rate: boolean
}
