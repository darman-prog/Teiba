import type { ReactNode } from 'react';
import { cn } from '../../lib/cn';

// Pastilla de instrumento: borde 1px, radio 4px, texto nunca en chlorophyll/signal.
export function Chip({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-[4px] border border-border bg-surface px-2 py-0.5 text-[12px] font-medium text-ink-2',
        className,
      )}
    >
      {children}
    </span>
  );
}
