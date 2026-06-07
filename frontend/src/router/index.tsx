import { createBrowserRouter } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { Login } from '@/pages/Login'
import { NotFound } from '@/pages/NotFound'
import { Placeholder } from '@/pages/Placeholder'

import { ProtectedRoute } from './ProtectedRoute'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: '/', element: <Placeholder title="Dashboard" /> },
          { path: '/accounts', element: <Placeholder title="Cuentas" /> },
          { path: '/transactions', element: <Placeholder title="Transacciones" /> },
          { path: '/currency', element: <Placeholder title="Tipo de cambio" /> },
          { path: '/shared', element: <Placeholder title="Gastos compartidos" /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
