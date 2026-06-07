import axios from 'axios'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/store/AuthContext'

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(email, password)
      navigate('/', { replace: true })
    } catch (err) {
      // Distinguir error de credenciales (401) de error de red.
      if (axios.isAxiosError(err) && err.response) {
        setError('Email o contraseña incorrectos.')
      } else {
        setError('No se pudo conectar con el servidor.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-cosmos px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        <div className="rounded-lg border border-horizon bg-nebula p-8 md:p-10">
          {/* Header: wordmark + franja argentina + tagline */}
          <header className="text-center">
            <h1 className="font-display font-extrabold text-4xl text-star">
              ZENIT<span className="text-celeste">H</span>
            </h1>
            {/* Franja argentina (único motivo de esta vista). */}
            <div className="mx-auto mt-3 flex h-0.5 w-10 overflow-hidden opacity-40">
              <div className="flex-1 bg-celeste" />
              <div className="flex-1 bg-star" />
              <div className="flex-1 bg-celeste" />
            </div>
            <p className="mt-2 font-body text-sm text-moon">Tu economía, clara.</p>
          </header>

          <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="vos@ejemplo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            {error && (
              <p role="alert" className="font-body text-sm text-error">
                {error}
              </p>
            )}

            <Button type="submit" disabled={loading} className="mt-2 w-full">
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Ingresando...
                </>
              ) : (
                'Ingresar'
              )}
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  )
}
