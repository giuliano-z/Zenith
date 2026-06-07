import { Label } from '@/components/ui/label'
import type { Account } from '@/types/account'
import type { Category } from '@/types/category'
import type { TransactionFilters as Filters, TransactionType } from '@/types/transaction'

const fieldClass =
  'flex w-full rounded-lg border border-horizon bg-orbit px-3 py-2 text-sm font-body text-star focus:outline-none focus:border-celeste focus:ring-2 focus:ring-celeste/15 transition-all duration-150'

const TYPE_OPTIONS: { value: TransactionType; label: string }[] = [
  { value: 'income', label: 'Ingreso' },
  { value: 'expense', label: 'Gasto' },
  { value: 'transfer_out', label: 'Transferencia enviada' },
  { value: 'transfer_in', label: 'Transferencia recibida' },
]

// Es transferencia → no aplica filtro por categoría (las transfers no la llevan).
function isTransfer(type?: TransactionType): boolean {
  return type === 'transfer_out' || type === 'transfer_in'
}

export function TransactionFilters({
  filters,
  accounts,
  categories,
  onChange,
  onClear,
}: {
  filters: Filters
  accounts: Account[]
  categories: Category[]
  // Cualquier cambio de filtro debe resetear a page=1 (lo hace el padre).
  onChange: (patch: Partial<Filters>) => void
  onClear: () => void
}) {
  const showCategory = !isTransfer(filters.transaction_type)

  return (
    <div className="rounded-lg border border-horizon bg-nebula p-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Cuenta */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-account">Cuenta</Label>
          <select
            id="f-account"
            className={fieldClass}
            value={filters.account_id ?? ''}
            onChange={(e) =>
              onChange({ account_id: e.target.value ? Number(e.target.value) : undefined })
            }
          >
            <option value="">Todas</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </div>

        {/* Tipo */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-type">Tipo</Label>
          <select
            id="f-type"
            className={fieldClass}
            value={filters.transaction_type ?? ''}
            onChange={(e) => {
              const value = (e.target.value || undefined) as TransactionType | undefined
              // Si pasa a transferencia, limpiamos la categoría seleccionada.
              onChange({
                transaction_type: value,
                ...(isTransfer(value) ? { category_id: undefined } : {}),
              })
            }}
          >
            <option value="">Todos</option>
            {TYPE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>

        {/* Categoría (oculta para transferencias) */}
        {showCategory && (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="f-category">Categoría</Label>
            <select
              id="f-category"
              className={fieldClass}
              value={filters.category_id ?? ''}
              onChange={(e) =>
                onChange({ category_id: e.target.value ? Number(e.target.value) : undefined })
              }
            >
              <option value="">Todas</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Desde */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-from">Desde</Label>
          <input
            id="f-from"
            type="date"
            className={fieldClass}
            value={filters.date_from ?? ''}
            onChange={(e) => onChange({ date_from: e.target.value || undefined })}
          />
        </div>

        {/* Hasta */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-to">Hasta</Label>
          <input
            id="f-to"
            type="date"
            className={fieldClass}
            value={filters.date_to ?? ''}
            onChange={(e) => onChange({ date_to: e.target.value || undefined })}
          />
        </div>
      </div>

      <button
        type="button"
        onClick={onClear}
        className="mt-4 text-sm font-medium text-celeste transition-colors duration-150 hover:text-celeste-bright"
      >
        Limpiar filtros
      </button>
    </div>
  )
}
