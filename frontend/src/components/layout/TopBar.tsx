import { Menu } from 'lucide-react'

// TopBar solo para mobile: en desktop el sidebar siempre visible la reemplaza.
export function TopBar({ onOpenMenu }: { onOpenMenu: () => void }) {
  return (
    <header className="flex items-center gap-3 border-b border-horizon bg-nebula px-4 py-3 md:hidden">
      <button
        type="button"
        onClick={onOpenMenu}
        aria-label="Abrir menú"
        className="rounded-lg p-2 text-moon transition-colors duration-150 hover:bg-orbit hover:text-star"
      >
        <Menu className="h-5 w-5" />
      </button>
      <span className="font-display font-bold text-lg text-star">
        ZENIT<span className="text-celeste">H</span>
      </span>
    </header>
  )
}
