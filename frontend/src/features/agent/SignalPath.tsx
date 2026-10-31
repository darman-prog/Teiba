import { useState } from 'react';
import { Route } from 'lucide-react';
import type { ChatMessage } from '../../hooks/useAgent';
import { SignalNode } from './SignalNode';

// Ruta de la señal: trazas del mensaje seleccionado, nunca turnos mezclados.
export function SignalPath({ message }: { message: ChatMessage | null }) {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  if (!message || message.failed || message.trazas.length === 0) {
    return (
      <div className="rounded-[8px] border border-dashed border-border bg-surface p-4">
        <p className="flex items-center gap-2 font-display text-[13px] font-semibold uppercase tracking-[0.08em] text-ink">
          <Route size={15} strokeWidth={1.5} aria-hidden="true" className="text-moss" />
          Ruta de la señal
        </p>
        <p className="mt-1 text-[13px] text-ink-2">
          Selecciona “Ver N trazas” en una respuesta para inspeccionar qué herramientas usó Sage y en qué orden.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-[8px] border border-border bg-surface p-3 md:p-4">
        <p className="flex items-center gap-2 font-display text-[13px] font-semibold uppercase tracking-[0.08em] text-ink">
          <Route size={15} strokeWidth={1.5} aria-hidden="true" className="text-moss" />
          Ruta de la señal · {message.trazas.length} {message.trazas.length === 1 ? 'herramienta' : 'herramientas'}
        </p>
        {message.traceId && (
          <p className="mt-0.5 font-mono text-[11px] text-ink-2">
            traceId: {message.traceId} <span className="font-sans">· identificador de la consulta</span>
          </p>
        )}
        <ol className="signal-rail mt-3 flex flex-col gap-2">
          {message.trazas.map((t, i) => (
            <SignalNode key={`${message.id}-${i}`} trace={t} index={i} open={openIdx === i} onToggle={() => setOpenIdx((v) => (v === i ? null : i))} />
          ))}
      </ol>
    </div>
  );
}
