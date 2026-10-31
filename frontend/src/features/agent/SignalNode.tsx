import { useId, useState } from 'react';
import { Check, ChevronDown, Copy, Wrench } from 'lucide-react';
import type { TraceItem } from '../../types/api';
import { cn } from '../../lib/cn';

// Nodo de la ruta: hilo copper con nodo chlorophyll, estado con icono + texto.
export function SignalNode({ trace, index, open, onToggle }: { trace: TraceItem; index: number; open: boolean; onToggle: () => void }) {
  // useId mantiene únicos los ids aunque la ruta se monte en varios breakpoints.
  const uid = useId();
  const btnId = `traza-btn-${uid}-${index}`;
  const panelId = `traza-panel-${uid}-${index}`;
  return (
    <li className="relative pl-8">
      <span
        aria-hidden="true"
        className={cn(
          'absolute left-[7px] top-4 size-3 rounded-full border-2 border-surface',
          trace.ok ? 'bg-chlorophyll' : 'bg-danger',
        )}
      />
      <div className="rounded-[6px] border border-border bg-surface">
        <button
          type="button"
          id={btnId}
          aria-expanded={open}
          aria-controls={open ? panelId : undefined}
          onClick={onToggle}
          className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left"
        >
          <Wrench size={15} strokeWidth={1.5} aria-hidden="true" className="shrink-0 text-moss" />
          <span className="min-w-0 flex-1">
            <span className="data-mono block truncate text-[13px] font-medium text-ink">{trace.tool}</span>
            <span className="block truncate text-[12px] text-ink-2">{trace.resumen}</span>
          </span>
          <span className="flex shrink-0 items-center gap-1.5">
            {trace.ok ? (
              <span className="inline-flex items-center gap-1 rounded-[4px] bg-success-soft px-1.5 py-0.5 text-[11px] font-semibold text-success">
                <Check size={12} strokeWidth={1.5} aria-hidden="true" /> ok · {trace.ms}ms
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 rounded-[4px] bg-danger-soft px-1.5 py-0.5 text-[11px] font-semibold text-danger">
                falla · {trace.ms}ms
              </span>
            )}
            <ChevronDown size={15} strokeWidth={1.5} aria-hidden="true" className={cn('text-ink-2 transition-transform', open && 'rotate-180')} />
          </span>
        </button>
        {open && <SignalDetail trace={trace} panelId={panelId} btnId={btnId} />}
      </div>
    </li>
  );
}

// Detalle con resultado crudo y scroll interno; el JSON es string, no objeto.
export function SignalDetail({ trace, panelId, btnId }: { trace: TraceItem; panelId: string; btnId: string }) {
  const [copiado, setCopiado] = useState(false);

  // Copia args + resultado para reutilizar la llamada fuera del panel.
  async function copiar() {
    const texto = `args: ${JSON.stringify(trace.args)}\nresultado: ${trace.resultado ?? '(sin resultado)'}`;
    try {
      await navigator.clipboard.writeText(texto);
      setCopiado(true);
      window.setTimeout(() => setCopiado(false), 1600);
    } catch {
      setCopiado(false);
    }
  }

  return (
    <div id={panelId} role="region" aria-labelledby={btnId} className="border-t border-border px-3 py-2">
      <div className="flex items-center justify-between gap-2">
        <p className="field-label">Argumentos</p>
        <button
          type="button"
          onClick={copiar}
          aria-live="polite"
          className="inline-flex min-h-[44px] items-center gap-1 rounded-[4px] px-2 text-[12px] font-semibold text-ink-2 hover:text-ink md:min-h-0 md:py-1"
        >
          {copiado ? <Check size={13} strokeWidth={1.5} aria-hidden="true" /> : <Copy size={13} strokeWidth={1.5} aria-hidden="true" />}
          {copiado ? 'Copiado' : 'Copiar'}
        </button>
      </div>
      <pre role="region" tabIndex={0} aria-label="Argumentos de la herramienta" className="data-mono mt-1 max-h-24 overflow-auto rounded-[4px] border border-border bg-mineral p-2 text-[12px] text-ink">
        {JSON.stringify(trace.args, null, 2)}
      </pre>
      <p className="field-label mt-2">Resultado crudo</p>
      <pre role="region" tabIndex={0} aria-label="Resultado crudo de la herramienta" className="data-mono mt-1 max-h-48 overflow-auto rounded-[4px] border border-border bg-ink p-2 text-[12px] leading-relaxed text-white">
        {trace.resultado ?? '(sin resultado)'}
      </pre>
    </div>
  );
}
