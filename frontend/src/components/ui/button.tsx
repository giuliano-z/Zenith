import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import * as React from 'react'

import { cn } from '@/lib/utils'

// Variantes alineadas a AUSTRAL (ver CLAUDE.austral.md). Celeste es el único acento.
const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-body font-bold transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-celeste/30 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-celeste text-void hover:bg-celeste-bright',
        secondary:
          'bg-transparent text-celeste border border-celeste font-semibold hover:bg-celeste-dim',
        ghost:
          'bg-transparent text-moon border border-horizon font-semibold hover:bg-orbit hover:text-star hover:border-horizon/70 transition-all',
        link: 'text-celeste underline-offset-4 hover:underline',
      },
      size: {
        default: 'px-5 py-2.5',
        sm: 'px-3 py-2 text-xs',
        lg: 'px-6 py-3 text-base',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    )
  }
)
Button.displayName = 'Button'

// eslint-disable-next-line react-refresh/only-export-components
export { Button, buttonVariants }
