import { Activity, AlertTriangle, Radio } from 'lucide-react';
import type { ChatMessage } from '../../hooks/useAgent';
import type { SensorItem } from '../../types/api';

// Placa de estación: resume nodos, alertas, traza y estado sin competir con la bitácora.
export function StationStrip({
  sensors,
  selected,
  loading,
}: {
  sensors: SensorItem[];
  selected: ChatMessage | null;
  loading: boolean;
}) {
  const alertas = sensors.filter((s) => s.estado === 'danger' || s.estado === 'warning').length;
  const trazas = selected?.trazas.length ?? 0;
  // El estado es un texto + icono; el color nunca es la única señal.
  const estado = loading ? 'MIDIENDO' : alertas > 0 ? 'ATENCIÓN' : 'OPERATIVA';
  const estadoCls = loading ? 'text-ink-2' : alertas > 0 ? 'text-warn' : 'text-success';
  const EstadoIcon = loading ? Activity : alertas > 0 ? AlertTriangle : Radio;

  return (
    <section aria-label="Estado de la estación" className="grid grid-cols-2 gap-px overflow-hidden rounded-[8px] border border-border bg-border md:grid-cols-5">
      <div className="bg-surface p-3">
        <p className="field-label">Estación</p>
        <p className="data-mono mt-1 text-[14px] font-semibold text-ink">SAGE-01</p>
      </div>
      <div className="bg-surface p-3">
        <p className="field-label">Nodos</p>
        <p className="data-mono mt-1 text-[14px] font-semibold text-ink">{String(sensors.length).padStart(2, '0')}</p>
      </div>
      <div className="bg-surface p-3">
        <p className="field-label">En revisión</p>
        <p className={`data-mono mt-1 text-[14px] font-semibold ${alertas > 0 ? 'text-warn' : 'text-ink'}`}>
          {String(alertas).padStart(2, '0')}
        </p>
      </div>
      <div className="bg-surface p-3">
        <p className="field-label">Traza</p>
        <p className="data-mono mt-1 text-[14px] font-semibold text-ink">{trazas > 0 ? String(trazas).padStart(2, '0') : '—'}</p>
      </div>
      <div className="col-span-2 bg-surface p-3 md:col-span-1">
        <p className="field-label">Estado</p>
        <p className={`mt-1 flex items-center gap-1.5 text-[13px] font-semibold ${estadoCls}`}>
          <EstadoIcon size={14} strokeWidth={1.5} aria-hidden="true" />
          <span className="data-mono">{estado}</span>
        </p>
      </div>
    </section>
  );
}
