import axios from 'axios'

// Clave única del token en localStorage (compartida con AuthContext).
export const TOKEN_KEY = 'zenith_token'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Request: si hay token, lo adjunta como Authorization: Token <hex> (esquema Knox).
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

// Response: ante un 401 (token vencido/inválido) limpia sesión y vuelve al login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      // Evita redirigir si ya estamos en /login (p. ej. credenciales inválidas).
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
