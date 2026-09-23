import { cn } from '@/lib/utils';
import { type VariantProps, cva } from 'class-variance-authority';
import type * as React from 'react';

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-blue-600/90 text-white shadow hover:bg-blue-600',
        secondary: 'border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700',
        destructive:
          'border-transparent bg-rose-950/70 text-rose-300 border border-rose-800/50 hover:bg-rose-900',
        outline: 'text-slate-300 border-slate-700 hover:bg-slate-800',
        success:
          'border-emerald-800/50 bg-emerald-950/60 text-emerald-300 shadow-sm hover:bg-emerald-900/60',
        warning:
          'border-amber-800/50 bg-amber-950/60 text-amber-300 shadow-sm hover:bg-amber-900/60',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
