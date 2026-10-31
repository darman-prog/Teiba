import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/cn';

// Superficie de campo: blanca, borde 1px, radio 8px, sin glassmorphism.
export function Surface({ className, children, ...rest }: HTMLAttributes<HTMLElement> & { children: ReactNode }) {
  return (
    <section {...rest} className={cn('rounded-[8px] border border-border bg-surface', className)}>
      {children}
    </section>
  );
}
