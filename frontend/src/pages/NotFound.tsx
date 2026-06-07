import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'

// 404 — fuera del AppShell, sobre cosmos a pantalla completa.
export function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-cosmos px-4 text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      >
        <p className="font-mono text-sm uppercase tracking-widest text-celeste">Error 404</p>
        <h1 className="mt-2 font-display font-extrabold text-7xl text-star">404</h1>
        <p className="mt-4 font-body text-moon">
          La página que buscás no existe o fue movida.
        </p>
        <Button asChild className="mt-8">
          <Link to="/">Volver al inicio</Link>
        </Button>
      </motion.div>
    </div>
  )
}
