import { Link } from 'react-router-dom';
import { MapPin } from 'lucide-react';
import type { ParqueResumen } from '../../types/api';
import { formatArea } from '../../lib/format';

// Tarjeta del libro: ficha sobria de herbario, sin mapa ni telemetría.
export function ParkCard({ parque }: { parque: ParqueResumen }) {
  return (
    <Link
      to={`/parques/${encodeURIComponent(parque.codigo)}`}
      aria-label={`Abrir ficha de ${parque.nombre}`}
      className="flex flex-col gap-2 rounded-[8px] border border-border bg-surface p-4 transition-colors hover:border-moss"
    >
      <span className="flex items-start justify-between gap-2">
        <span className="font-display text-[16px] font-semibold leading-snug text-ink">{parque.nombre}</span>
        <span className="data-mono shrink-0 rounded-[4px] border border-border bg-mineral px-1.5 py-0.5 text-[12px] text-ink-2">
          {parque.codigo}
        </span>
      </span>
      <span className="flex items-center gap-1.5 text-[13px] text-ink-2">
        <MapPin size={14} strokeWidth={1.5} aria-hidden="true" className="shrink-0" />
        <span className="truncate">
          {parque.comuna ?? 'Comuna sin dato'}
          {parque.direccion ? ` · ${parque.direccion}` : ''}
        </span>
      </span>
      <span className="flex flex-wrap gap-1.5 border-t border-border pt-2 text-[12px]">
        {parque.tipo_parque && (
          <span className="rounded-[4px] bg-mineral px-1.5 py-0.5 font-medium text-ink-2">{parque.tipo_parque}</span>
        )}
        {parque.estado_general && (
          <span className="rounded-[4px] bg-mineral px-1.5 py-0.5 font-medium text-ink-2">{parque.estado_general}</span>
        )}
        <span className="rounded-[4px] bg-mineral px-1.5 py-0.5 font-medium text-ink-2">
          {parque.total_sectores} {parque.total_sectores === 1 ? 'sector' : 'sectores'} · {formatArea(parque.area_m2)}
        </span>
      </span>
    </Link>
  );
}
