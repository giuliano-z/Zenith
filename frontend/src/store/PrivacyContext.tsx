import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

const PRIVACY_KEY = 'zenith_privacy'

interface PrivacyContextValue {
  isPrivate: boolean
  toggle: () => void
}

const PrivacyContext = createContext<PrivacyContextValue | undefined>(undefined)

// Modo privacidad: oculta todos los montos financieros (ver useMoney). Es una
// preferencia de presentación, independiente de la autenticación.
export function PrivacyProvider({ children }: { children: ReactNode }) {
  const [isPrivate, setIsPrivate] = useState<boolean>(
    () => localStorage.getItem(PRIVACY_KEY) === 'true'
  )

  const toggle = useCallback(() => {
    setIsPrivate((prev) => {
      const next = !prev
      localStorage.setItem(PRIVACY_KEY, String(next))
      return next
    })
  }, [])

  const value = useMemo<PrivacyContextValue>(() => ({ isPrivate, toggle }), [isPrivate, toggle])

  return <PrivacyContext.Provider value={value}>{children}</PrivacyContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePrivacy(): PrivacyContextValue {
  const ctx = useContext(PrivacyContext)
  if (!ctx) {
    throw new Error('usePrivacy debe usarse dentro de <PrivacyProvider>')
  }
  return ctx
}
