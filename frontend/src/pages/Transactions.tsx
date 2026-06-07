import { ChevronLeft, ChevronRight, Filter, Plus } from 'lucide-react'
import { useMemo, useState } from 'react'

import { ErrorState } from '@/components/common/states'
import { CreateTransactionModal } from '@/components/transactions/CreateTransactionModal'
import { TransactionFilters } from '@/components/transactions/TransactionFilters'
import { TransactionList } from '@/components/transactions/TransactionList'
import { Button } from '@/components/ui/button'
import { useAccounts } from '@/hooks/useAccounts'
import { useCategories } from '@/hooks/useCategories'
import { useTransactions } from '@/hooks/useTransactions'
import type { Account } from '@/types/account'
import type { Category } from '@/types/category'
import type { TransactionFilters as Filters } from '@/types/transaction'

const PAGE_SIZE = 20 // StandardPagination del backend (RF-011)

export function Transactions() {
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<Filters>({ page: 1 })

  const { data: accounts = [] } = useAccounts()
  const { data: categories = [] } = useCategories()
  const { data, isPending, isError, refetch } = useTransactions(filters)

  // Mapas id → entidad para resolver los IDs que devuelve la API de transacciones.
  const accountsById = useMemo(
    () => new Map<number, Account>(accounts.map((a) => [a.id, a])),
    [accounts],
  )
  const categoriesById = useMemo(
    () => new Map<number, Category>(categories.map((c) => [c.id, c])),
    [categories],
  )

  // Cualquier cambio de filtro vuelve a page=1 (RF-011).
  function patchFilters(patch: Partial<Filters>) {
    setFilters((prev) => ({ ...prev, ...patch, page: 1 }))
  }

  function clearFilters() {
    setFilters({ page: 1 })
  }

  function goToPage(page: number) {
    setFilters((prev) => ({ ...prev, page }))
  }

  const currentPage = filters.page ?? 1
  const totalPages = data ? Math.max(1, Math.ceil(data.count / PAGE_SIZE)) : 1

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display font-bold text-2xl text-star">Transacciones</h1>
        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={() => setShowFilters((s) => !s)}>
            <Filter className="h-4 w-4" />
            Filtros
          </Button>
          <CreateTransactionModal
            accounts={accounts}
            trigger={
              <Button>
                <Plus className="h-4 w-4" />
                Nueva transacción
              </Button>
            }
          />
        </div>
      </header>

      {showFilters && (
        <TransactionFilters
          filters={filters}
          accounts={accounts}
          categories={categories}
          onChange={patchFilters}
          onClear={clearFilters}
        />
      )}

      {isError ? (
        <ErrorState onRetry={() => void refetch()} />
      ) : (
        <>
          <TransactionList
            transactions={data?.results ?? []}
            accountsById={accountsById}
            categoriesById={categoriesById}
            isLoading={isPending}
          />

          {/* Paginación: oculta si hay una sola página o no hay datos aún. */}
          {data && data.count > 0 && totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-horizon pt-4">
              <Button
                variant="ghost"
                size="sm"
                disabled={currentPage <= 1}
                onClick={() => goToPage(currentPage - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
                Anterior
              </Button>
              <span className="font-body text-sm text-moon">
                Página {currentPage} de {totalPages}
              </span>
              <Button
                variant="ghost"
                size="sm"
                disabled={currentPage >= totalPages}
                onClick={() => goToPage(currentPage + 1)}
              >
                Siguiente
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
