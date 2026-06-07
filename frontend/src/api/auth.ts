import { api } from '@/api/axios'
import type { AuthToken, LoginCredentials } from '@/types/auth'

// RF-002: autentica por email + contraseña. Knox devuelve { token, expiry }.
export async function login(credentials: LoginCredentials): Promise<AuthToken> {
  const { data } = await api.post<AuthToken>('/api/auth/login/', credentials)
  return data
}

// RF-003: invalida el token actual en el backend. El header lo agrega el interceptor.
export async function logout(): Promise<void> {
  await api.post('/api/auth/logout/')
}
