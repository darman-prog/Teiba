import { Battery, Thermometer, Droplets } from 'lucide-react';
import type { SensorItem } from '../../types/api';
import { formatAntiguedad, formatNumero } from '../../lib/format';
import { StatusTag } from './StatusTag';

// Ficha de instrumento del transecto: número de nodo, ID mono, sector,
// rejilla de lecturas y pie; clic precarga la bitácora.
export function SensorCard({
  sensor,
  index,
  onAsk,
  idPrefix = 'sensor',
}: {
  sensor: SensorItem;
  index: number;
  onAsk?: (sensorId: string) => void;
  idPrefix?: string;
}) {
  const lec = sensor.ultima_lectura;
  const sectorId = `${idPrefix}-sector-${sensor.id}`;
  const lecturaId = `${idPrefix}-lectura-${sensor.id}`;
  // Número de nodo en base 01: el transecto se lee como riel de estación.
  const nodo = String(index + 1).padStart(2, '0');
  return (
    <button
      type="button"
      onClick={() => onAsk?.(sensor.id)}
      aria-describedby={`${sectorId} ${lecturaId}`}
      className="relative mt-2 flex min-w-[228px] max-w-[260px] flex-1 snap-start flex-col gap-2 rounded-[8px] border border-border bg-surface p-3 pt-4 text-left transition-colors hover:border-moss focus-visible:outline-2 xl:min-w-[204px]"
    >
      <span aria-hidden="true" className="absolute -top-2.5 left-3 rounded-[4px] bg-moss px-1.5 py-px font-mono text-[11px] font-semibold text-white">
        {nodo}
      </span>
      <span className="sr-only">Preguntar por el sensor {sensor.id}. </span>
      <span className="flex items-center justify-between gap-2">
        <span className="data-mono text-[15px] font-medium text-ink">{sensor.id}</span>
        <StatusTag estado={sensor.estado} />
      </span>
      <span id={sectorId} className="line-clamp-2 min-h-[2.4em] text-[13px] leading-snug text-ink-2">{sensor.sector ?? 'Sector sin nombre'}</span>
      <span id={lecturaId} className="grid grid-cols-3 gap-1 border-t border-border pt-2 text-[12px]">
        <span className="flex items-center gap-1 text-ink-2">
          <Droplets size={13} strokeWidth={1.5} aria-hidden="true" />
          <span className="data-mono text-ink">{lec?.ph != null ? `pH ${formatNumero(lec.ph)}` : 'pH —'}</span>
        </span>
        <span className="flex items-center gap-1 text-ink-2">
          <Thermometer size={13} strokeWidth={1.5} aria-hidden="true" />
          <span className="data-mono text-ink">{lec?.temperatura != null ? `${formatNumero(lec.temperatura)}°` : '—'}</span>
        </span>
        <span className="flex items-center gap-1 text-ink-2">
          <Battery size={13} strokeWidth={1.5} aria-hidden="true" />
          <span className="data-mono text-ink">{lec?.bateria != null ? `${lec.bateria}%` : '—'}</span>
        </span>
      </span>
      <span className="font-mono text-[11px] text-ink-2">
        {lec?.timestamp ? formatAntiguedad(lec.antiguedad_min) : 'sin lecturas'}
        {sensor.depende_de ? ` · ${sensor.depende_de}` : ''}
      </span>
    </button>
  );
}
