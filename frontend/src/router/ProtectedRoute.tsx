import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '@/store/AuthContext'

// Guard de autenticación: sin token → /login. Con token, renderiza la ruta hija.
export function ProtectedRoute() {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
