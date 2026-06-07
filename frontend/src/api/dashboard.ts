import { api } from '@/api/axios'
import type { Dashboard } from '@/types/dashboard'

// RF-019/RF-020: resumen financiero del período. month en 1..12.
export async function getDashboard(year: number, month: number): Promise<Dashboard> {
  const { data } = await api.get<Dashboard>('/api/dashboard/', {
    params: { year, month },
  })
  return data
}
