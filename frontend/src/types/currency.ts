// Contrato del módulo CURRENCY (apps/currency/serializers.py + views.py).

export type RateType = 'blue' | 'oficial' | 'tarjeta' | 'custom'
export type RateSource = 'dolarapi' | 'manual'

// Las claves de cotización en vivo (las que /fetch/ devuelve en el caso OK).
export type LiveRateKey = 'blue' | 'oficial' | 'tarjeta'

export interface LiveRate {
  rate: string
  source: string
}

// Respuesta de GET /fetch/. En el caso OK trae las tres; en fallback, una sola.
export interface LiveRates {
  blue?: LiveRate
  oficial?: LiveRate
  tarjeta?: LiveRate
  fetched_at: string
  is_fallback: boolean
}

// Una cotización guardada (GET /rates/). No incluye el autor (ver serializer).
export interface ExchangeRate {
  id: number
  rate_type: RateType
  rate: string
  effective_date: string // YYYY-MM-DD
  source: RateSource
  created_at: string
}

export interface SaveRatePayload {
  rate_type: RateType
  rate: string
  effective_date: string
  source: RateSource
}
