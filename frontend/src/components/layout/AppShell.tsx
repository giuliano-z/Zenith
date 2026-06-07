import { AnimatePresence, motion } from 'framer-motion'
import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

// Shell de la app: sidebar fijo en desktop, drawer en mobile + main scrollable.
export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar fijo (desktop) */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* Drawer (mobile) */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              onClick={() => setMobileOpen(false)}
              className="fixed inset-0 z-40 bg-void/70 md:hidden"
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="fixed inset-y-0 left-0 z-50 md:hidden"
            >
              <Sidebar onNavigate={() => setMobileOpen(false)} />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Columna de contenido */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar onOpenMenu={() => setMobileOpen(true)} />
        <main className="flex-1 overflow-auto bg-cosmos p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
