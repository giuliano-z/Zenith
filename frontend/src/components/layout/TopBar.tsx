import { Eye, EyeOff, Menu } from 'lucide-react'

import { usePrivacy } from '@/store/PrivacyContext'

// TopBar visible siempre. El hamburger solo aparece en mobile (en desktop el
// sidebar fijo lo reemplaza); el toggle de privacidad está disponible siempre.
export function TopBar({ onOpenMenu }: { onOpenMenu: () => void }) {
  const { isPrivate, toggle } = usePrivacy()

  return (
    <header className="flex items-center gap-3 border-b border-horizon bg-nebula px-4 py-3">
      <button
        type="button"
        onClick={onOpenMenu}
        aria-label="Abrir menú"
        className="rounded-lg p-2 text-moon transition-colors duration-150 hover:bg-orbit hover:text-star md:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>

      <span className="font-display font-bold text-lg text-star md:hidden">
        ZENIT<span className="text-celeste">H</span>
      </span>

      {/* Toggle de privacidad: oculta/muestra todos los montos. */}
      <button
        type="button"
        onClick={toggle}
        aria-label={isPrivate ? 'Mostrar montos' : 'Ocultar montos'}
        aria-pressed={isPrivate}
        title={isPrivate ? 'Mostrar montos' : 'Ocultar montos'}
        className="ml-auto flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-body font-semibold text-moon transition-colors duration-150 hover:bg-orbit hover:text-star"
      >
        {isPrivate ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        <span className="hidden sm:inline">{isPrivate ? 'Mostrar' : 'Ocultar'}</span>
      </button>
    </header>
  )
}
