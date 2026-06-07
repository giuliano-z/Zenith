import { useQuery } from '@tanstack/react-query'

import { getCategories } from '@/api/categories'
import type { CategoryType } from '@/types/category'

// RF-014: categorías para el selector. Datos casi estáticos (sembrados por
// migración), por eso staleTime infinito: no hace falta refetchear.
export function useCategories(categoryType?: CategoryType) {
  return useQuery({
    queryKey: ['categories', categoryType ?? 'all'],
    queryFn: () => getCategories(categoryType),
    staleTime: Infinity,
  })
}
