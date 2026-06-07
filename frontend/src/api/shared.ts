import { api } from '@/api/axios'
import type {
  CreateSharedExpensePayload,
  SharedBalance,
  SharedExpense,
  SettlePayload,
} from '@/types/shared'

// RF-022: historial completo de gastos compartidos (settled + unsettled).
export async function getSharedExpenses(): Promise<SharedExpense[]> {
  const { data } = await api.get<SharedExpense[]>('/api/shared/expenses/')
  return data
}

// RF-022: registra un gasto compartido. El pagador es request.user (sin campo).
export async function createSharedExpense(
  payload: CreateSharedExpensePayload,
): Promise<SharedExpense> {
  const { data } = await api.post<SharedExpense>('/api/shared/expenses/', payload)
  return data
}

// RF-023: balance neto actual entre los dos usuarios.
export async function getSharedBalance(): Promise<SharedBalance> {
  const { data } = await api.get<SharedBalance>('/api/shared/balance/')
  return data
}

// RF-024: salda el balance. Body vacío = marcar saldado sin mover fondos.
export async function settleBalance(payload: SettlePayload = {}): Promise<unknown> {
  const { data } = await api.post('/api/shared/balance/settle/', payload)
  return data
}
