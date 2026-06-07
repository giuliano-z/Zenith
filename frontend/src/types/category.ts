// Contrato de /api/categories/ (apps/transactions/serializers.py → CategorySerializer).

export type CategoryType = 'income' | 'expense'

export interface Category {
  id: number
  name: string
  category_type: CategoryType
  color: string
}
