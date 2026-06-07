import { createBrowserRouter } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { Accounts } from '@/pages/Accounts'
import { Currency } from '@/pages/Currency'
import { Dashboard } from '@/pages/Dashboard'
import { Login } from '@/pages/Login'
import { NotFound } from '@/pages/NotFound'
import { SharedExpenses } from '@/pages/SharedExpenses'
import { Transactions } from '@/pages/Transactions'

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
          { path: '/', element: <Dashboard /> },
          { path: '/accounts', element: <Accounts /> },
          { path: '/transactions', element: <Transactions /> },
          { path: '/currency', element: <Currency /> },
          { path: '/shared', element: <SharedExpenses /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
