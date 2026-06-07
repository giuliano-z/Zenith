import { motion } from 'framer-motion'

// Placeholder AUSTRAL para las páginas de datos (Dashboard, Cuentas, etc.).
// Se reemplazan con las implementaciones reales en las fases 8b/8c/8d.
export function Placeholder({ title }: { title: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="mx-auto max-w-3xl"
    >
      <h1 className="font-display font-extrabold text-4xl text-star">{title}</h1>
      {/* Franja argentina (único motivo de esta vista). */}
      <div className="mt-3 flex h-0.5 w-10 overflow-hidden opacity-40">
        <div className="flex-1 bg-celeste" />
        <div className="flex-1 bg-star" />
        <div className="flex-1 bg-celeste" />
      </div>
      <p className="mt-6 font-body text-moon">Próximamente.</p>
    </motion.div>
  )
}
