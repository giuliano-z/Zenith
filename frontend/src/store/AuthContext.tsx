import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

import { TOKEN_KEY } from '@/api/axios'
import * as authApi from '@/api/auth'
import type { User } from '@/types/auth'

const EMAIL_KEY = 'zenith_email'

interface AuthContextValue {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(() => {
    const email = localStorage.getItem(EMAIL_KEY)
    return email ? { email } : null
  })

  // login() → POST /api/auth/login/ → guarda token + email. La redirección la
  // maneja la página de Login según el resultado.
  const login = useCallback(async (email: string, password: string) => {
    const { token: newToken } = await authApi.login({ email, password })
    localStorage.setItem(TOKEN_KEY, newToken)
    localStorage.setItem(EMAIL_KEY, email)
    setToken(newToken)
    setUser({ email })
  }, [])

  // logout() → intenta invalidar el token en el backend, pero siempre limpia
  // el estado local (aunque la red falle).
  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(EMAIL_KEY)
      setToken(null)
      setUser(null)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ token, user, isAuthenticated: Boolean(token), login, logout }),
    [token, user, login, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return ctx
}
