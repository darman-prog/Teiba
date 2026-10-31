import { useId } from 'react';
import { RefreshCw } from 'lucide-react';
import type { SensorItem } from '../../types/api';
import { SensorCard } from './SensorCard';
import { Button } from '../../shared/ui/Button';

// Transecto horizontal de sensores con scroll + snap en móvil.
export function SensorStrip({
  items,
  loading,
  onAsk,
  onRefresh,
  label,
}: {
  items: SensorItem[];
  loading: boolean;
  onAsk: (sensorId: string) => void;
  onRefresh: () => void;
  label?: string;
}) {
  // El transecto puede montarse en desktop y móvil; los ids no deben colisionar.
  const uid = useId();
  const headingId = `transecto-titulo-${uid}`;
  const itemPrefix = `sensor-${uid}`;
  return (
    <section aria-label={label} aria-labelledby={label ? undefined : headingId} className="rounded-[8px] border border-border bg-surface p-3 md:p-4">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div>
          <h2 id={headingId} className="font-display text-[13px] font-semibold uppercase tracking-[0.08em] text-ink">
            Transecto de sensores
          </h2>
          <p className="text-[12px] text-ink-2">
            Toca un nodo para preguntar por él en la bitácora.{' '}
            {items.length > 0 && (
              <span className="font-mono font-semibold uppercase text-moss">
                {String(items.length).padStart(2, '0')} nodos · {items.filter((s) => s.estado === 'danger' || s.estado === 'warning').length} en revisión
              </span>
            )}
          </p>
        </div>
        <Button variant="ghost" onClick={onRefresh} aria-label="Actualizar sensores" title="Actualizar">
          <RefreshCw size={15} strokeWidth={1.5} aria-hidden="true" />
          <span>Actualizar</span>
        </Button>
      </div>
      {loading ? (
        <div className="transect-scroll flex gap-2 overflow-x-auto pb-1" aria-hidden="true">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skeleton h-[132px] min-w-[228px] flex-1 rounded-[8px]" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="rounded-[6px] border border-dashed border-border px-3 py-4 text-[14px] text-ink-2">
          Sin sensores para este filtro. Revisa el seed de demo.
        </p>
      ) : (
        <div
          className="transect-scroll flex gap-2 overflow-x-auto pb-1 pt-2"
          role="list"
          tabIndex={0}
          aria-label="Sensores de calidad de suelo; desplázate para ver todos"
        >
          {items.map((s, i) => (
            <div key={s.id} role="listitem" className="contents">
              <SensorCard sensor={s} index={i} onAsk={onAsk} idPrefix={itemPrefix} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
