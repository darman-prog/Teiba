import { Sprout } from 'lucide-react';
import type { ParqueSector } from '../../types/api';

// Sectores de la ficha: nombre, tipo de suelo y zona de riesgo.
export function SectorList({ sectores }: { sectores: ParqueSector[] }) {
  if (sectores.length === 0) return <p className="text-[14px] text-ink-2">Este parque aún no registra sectores.</p>;
  return (
    <ul className="flex flex-col gap-1.5">
      {sectores.map((s, i) => (
        <li key={s.codigo ?? `${s.nombre}-${i}`} className="flex items-start gap-2 rounded-[6px] border border-border bg-surface px-3 py-2">
          <Sprout size={15} strokeWidth={1.5} aria-hidden="true" className="mt-0.5 shrink-0 text-moss" />
          <span>
            <span className="block text-[14px] font-semibold text-ink">{s.nombre}</span>
            <span className="block text-[12px] text-ink-2">
              {[s.codigo, s.tipo_suelo && `suelo ${s.tipo_suelo}`, s.zona_riesgo && `riesgo ${s.zona_riesgo}`].filter(Boolean).join(' · ')}
            </span>
          </span>
        </li>
      ))}
    </ul>
  );
}
