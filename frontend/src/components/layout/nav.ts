import { ArrowLeftRight, BarChart3, DollarSign, Users, Wallet, type LucideIcon } from 'lucide-react'

// Ítems de navegación del sidebar (las páginas de datos llegan en fases 8b/8c/8d).
export interface NavItem {
  label: string
  to: string
  icon: LucideIcon
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', to: '/', icon: BarChart3 },
  { label: 'Cuentas', to: '/accounts', icon: Wallet },
  { label: 'Transacciones', to: '/transactions', icon: ArrowLeftRight },
  { label: 'Tipo de cambio', to: '/currency', icon: DollarSign },
  { label: 'Gastos compartidos', to: '/shared', icon: Users },
]
