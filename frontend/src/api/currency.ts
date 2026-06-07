import { api } from '@/api/axios'
import type { ExchangeRate, LiveRates, SaveRatePayload } from '@/types/currency'

// RF-017: cotización en vivo desde DolarAPI (no persiste). 503 si no hay datos.
export async function fetchLiveRates(): Promise<LiveRates> {
  const { data } = await api.get<LiveRates>('/api/currency/fetch/')
  return data
}

// RF-018: historial global de tasas guardadas (sin paginar, ya ordenado desc).
export async function getRatesHistory(): Promise<ExchangeRate[]> {
  const { data } = await api.get<ExchangeRate[]>('/api/currency/rates/')
  return data
}

// RF-017: guarda una cotización (manual o tomada de la cotización en vivo).
export async function saveRate(payload: SaveRatePayload): Promise<ExchangeRate> {
  const { data } = await api.post<ExchangeRate>('/api/currency/rates/', payload)
  return data
}
