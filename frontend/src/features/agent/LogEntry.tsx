import { Route } from 'lucide-react';
import type { ReactNode } from 'react';
import type { ChatMessage } from '../../hooks/useAgent';
import { COPY } from '../../lib/copy';
import { cn } from '../../lib/cn';
import { Button } from '../../shared/ui/Button';

// Fila de bitácora: secuencia + nodo a la izquierda, registro a la derecha.
function LedgerRow({
  index,
  tone,
  label,
  live = false,
  children,
}: {
  index: number;
  tone: 'user' | 'sage' | 'error';
  label: string;
  live?: boolean;
  children: ReactNode;
}) {
  const seq = String(index + 1).padStart(2, '0');
  return (
    <article
      aria-label={label}
      aria-live={live ? 'polite' : undefined}
      aria-atomic={live ? true : undefined}
      className="relative grid grid-cols-[2rem_1fr] gap-3 border-b border-border py-3 last:border-b-0"
    >
      <div className="relative flex flex-col items-center">
        <span className="data-mono text-[11px] text-ink-2">{seq}</span>
        <span
          aria-hidden="true"
          className={cn('mt-2 size-2 rounded-full', tone === 'user' ? 'bg-moss' : tone === 'error' ? 'bg-danger' : 'bg-ink-2')}
        />
      </div>
      <div>{children}</div>
    </article>
  );
}

// Entrada de bitácora: registro de campo, no burbuja de chat genérica.
export function LogEntry({
  message,
  index,
  selected,
  onSelect,
  live = false,
}: {
  message: ChatMessage;
  index: number;
  selected: boolean;
  onSelect: (id: string) => void;
  live?: boolean;
}) {
  if (message.failed) {
    return (
      <LedgerRow index={index} tone="error" label="Registro de error">
        <div className="rounded-[6px] border border-danger/40 bg-danger-soft/40 p-3">
          <p className="field-label">Sage · sin registro</p>
          <p className="mt-1 text-[14px] text-ink">No se pudo completar el registro. Usa Reintentar en el aviso.</p>
        </div>
      </LedgerRow>
    );
  }
  if (message.role === 'user') {
    return (
      <LedgerRow index={index} tone="user" label="Pregunta del operador">
        <div className="rounded-[6px] border border-border bg-mineral/40 p-3">
          <p className="field-label flex items-center gap-1.5">
            <span aria-hidden="true" className="inline-block size-1.5 rotate-45 bg-moss" />
            Operador · pregunta
          </p>
          <p className="mt-1 text-[14px] font-medium text-ink">{message.texto}</p>
        </div>
      </LedgerRow>
    );
  }
  const n = message.trazas.length;
  return (
    <LedgerRow index={index} tone="sage" label="Respuesta de Sage" live={live}>
      <div className="rounded-[6px] border border-border bg-surface p-3">
        <p className="field-label">Sage · respuesta</p>
        <p className="mt-1 max-w-prose text-[15px] leading-relaxed text-ink">{message.texto}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2 border-t border-border pt-2">
          {message.meta && (
            <span className="font-mono text-[11px] text-ink-2">
              {message.meta.pasos} {message.meta.pasos === 1 ? 'paso' : 'pasos'} · {(message.meta.duracion_ms / 1000).toFixed(1)}s
              {message.meta.cached ? ' · caché' : ''}
            </span>
          )}
          {n > 0 && (
            <Button variant={selected ? 'primary' : 'secondary'} onClick={() => onSelect(message.id)} aria-pressed={selected}>
              <Route size={14} strokeWidth={1.5} aria-hidden="true" />
              {COPY.verTrazas(n)}
            </Button>
          )}
        </div>
      </div>
    </LedgerRow>
  );
}
