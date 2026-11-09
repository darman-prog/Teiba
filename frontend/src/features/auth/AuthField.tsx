import type { InputHTMLAttributes } from 'react';
import { FieldLabel } from '../../shared/ui/FieldLabel';
import { cn } from '../../lib/cn';

interface AuthFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
}

// Campo de acceso: label real, error anunciado y objetivo táctil de 44px.
export function AuthField({ id, label, hint, error, className, ...rest }: AuthFieldProps) {
  const describedBy =
    [hint ? `${id}-hint` : null, error ? `${id}-error` : null].filter(Boolean).join(' ') ||
    undefined;

  return (
    <div className="flex flex-col gap-1">
      <FieldLabel htmlFor={id}>{label}</FieldLabel>
      <input
        id={id}
        aria-describedby={describedBy}
        aria-invalid={error ? true : undefined}
        className={cn(
          'min-h-[44px] rounded-[6px] border bg-surface px-3 py-2 text-[14px] text-ink placeholder:text-ink-2/70 disabled:opacity-60',
          error ? 'border-danger' : 'border-border',
          className,
        )}
        {...rest}
      />
      {hint && (
        <p id={`${id}-hint`} className="text-[12px] text-ink-2">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="text-[12px] font-semibold text-danger">
          {error}
        </p>
      )}
    </div>
  );
}
