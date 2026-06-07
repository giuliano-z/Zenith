import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'

import { router } from '@/router'
import { AuthProvider } from '@/store/AuthContext'
import { PrivacyProvider } from '@/store/PrivacyContext'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <PrivacyProvider>
          <RouterProvider router={router} />
        </PrivacyProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}
