import { api } from '@/api/axios'
import type {
  CreateInstallmentPayload,
  CreateTransactionPayload,
  CreateTransferPayload,
  Paginated,
  Transaction,
  TransactionFilters,
} from '@/types/transaction'

// Quita las claves con valor undefined para no mandar query params vacíos.
function cleanParams(filters: TransactionFilters): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params[key] = value
    }
  }
  return params
}

// RF-011: lista paginada de transacciones del usuario con filtros opcionales.
export async function getTransactions(
  filters: TransactionFilters = {},
): Promise<Paginated<Transaction>> {
  const { data } = await api.get<Paginated<Transaction>>('/api/transactions/', {
    params: cleanParams(filters),
  })
  return data
}

// RF-009: registra una transacción simple (income/expense).
export async function createTransaction(
  payload: CreateTransactionPayload,
): Promise<Transaction> {
  const { data } = await api.post<Transaction>('/api/transactions/', payload)
  return data
}

// RF-009: registra una transferencia entre cuentas propias (par vinculado).
export async function createTransfer(payload: CreateTransferPayload): Promise<unknown> {
  const { data } = await api.post('/api/transactions/transfer/', payload)
  return data
}

// RF-010: registra una compra en cuotas (genera N transacciones EXPENSE).
export async function createInstallment(
  payload: CreateInstallmentPayload,
): Promise<unknown> {
  const { data } = await api.post('/api/transactions/installment/', payload)
  return data
}
