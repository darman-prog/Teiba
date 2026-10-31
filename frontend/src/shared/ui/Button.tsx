import type { ButtonHTMLAttributes } from 'react';
import { cn } from '../../lib/cn';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';

const styles: Record<Variant, string> = {
  primary: 'bg-moss text-white hover:bg-moss-deep disabled:bg-border disabled:text-ink-2',
  secondary: 'border border-border bg-surface text-ink hover:border-moss hover:text-moss disabled:opacity-60',
  ghost: 'text-ink-2 hover:text-ink hover:bg-neutral-soft disabled:opacity-60',
  danger: 'border border-danger bg-danger-soft text-danger hover:bg-danger hover:text-white disabled:opacity-60',
};

// Botón de instrumento: radio 6px, borde 1px, mínimo táctil 44px en móvil.
export function Button({
  variant = 'primary',
  className,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      {...rest}
      className={cn(
        'inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-[6px] px-3.5 py-2 text-[14px] font-semibold transition-colors md:min-h-0 md:py-1.5 focus-visible:outline-2',
        styles[variant],
        className,
      )}
    />
  );
}
