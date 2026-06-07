import { api } from '@/api/axios'
import type { Category, CategoryType } from '@/types/category'

// RF-014: lista las categorías visibles del usuario (sistema + propias).
// Filtra por tipo (income/expense) cuando se especifica.
export async function getCategories(categoryType?: CategoryType): Promise<Category[]> {
  const { data } = await api.get<Category[]>('/api/categories/', {
    params: categoryType ? { category_type: categoryType } : undefined,
  })
  return data
}
