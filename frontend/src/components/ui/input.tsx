import * as React from 'react'

import { cn } from '@/lib/utils'

// Input AUSTRAL: bg-orbit, foco celeste con ring sutil (ver CLAUDE.austral.md).
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex w-full rounded-lg border border-horizon bg-orbit px-3 py-2.5 text-sm font-body text-star',
          'placeholder:text-dusk',
          'focus:outline-none focus:border-celeste focus:ring-2 focus:ring-celeste/15',
          'disabled:cursor-not-allowed disabled:opacity-50',
          'transition-all duration-150',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }
