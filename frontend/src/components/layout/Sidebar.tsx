import { LogOut } from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { cn } from '@/lib/utils'
import { useAuth } from '@/store/AuthContext'

import { NAV_ITEMS } from './nav'

// Sidebar de navegación AUSTRAL. `onNavigate` permite cerrar el drawer en mobile.
export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const { user, logout } = useAuth()

  return (
    <aside className="flex h-full w-64 flex-col border-r border-horizon bg-nebula">
      {/* Header: wordmark + franja argentina (único motivo de esta vista). */}
      <div className="px-5 py-6">
        <span className="font-display font-bold text-xl text-star">
          ZENIT<span className="text-celeste">H</span>
        </span>
        <div className="mt-2 flex h-0.5 w-8 overflow-hidden opacity-40">
          <div className="flex-1 bg-celeste" />
          <div className="flex-1 bg-star" />
          <div className="flex-1 bg-celeste" />
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-1 flex-col gap-1 px-3">
        {NAV_ITEMS.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-body font-semibold transition-colors duration-150',
                isActive
                  ? 'bg-celeste-dim text-celeste'
                  : 'text-moon hover:bg-orbit hover:text-star'
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer: usuario + logout */}
      <div className="border-t border-horizon p-3">
        {user && (
          <p className="truncate px-3 pb-2 text-xs font-body text-dusk" title={user.email}>
            {user.email}
          </p>
        )}
        <button
          type="button"
          onClick={() => void logout()}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-body font-semibold text-moon transition-colors duration-150 hover:bg-orbit hover:text-star"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}
