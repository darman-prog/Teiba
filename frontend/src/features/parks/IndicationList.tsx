import { Info, TriangleAlert } from 'lucide-react';
import type { Indicacion } from '../../types/api';

// Indicaciones de manejo: icono + texto, nunca solo color.
export function IndicationList({ indicaciones }: { indicaciones: Indicacion[] }) {
  if (indicaciones.length === 0) return null;
  return (
    <ul className="flex flex-col gap-1.5" aria-label="Indicaciones de manejo">
      {indicaciones.map((it, i) => (
        <li
          key={i}
          className={
            it.nivel === 'warning'
              ? 'flex items-start gap-2 rounded-[6px] border border-warn/40 bg-warn-soft px-3 py-2 text-[13px] text-ink'
              : 'flex items-start gap-2 rounded-[6px] border border-water/40 bg-[#EEF5F5] px-3 py-2 text-[13px] text-ink'
          }
        >
          {it.nivel === 'warning' ? (
            <TriangleAlert size={15} strokeWidth={1.5} aria-hidden="true" className="mt-0.5 shrink-0 text-warn" />
          ) : (
            <Info size={15} strokeWidth={1.5} aria-hidden="true" className="mt-0.5 shrink-0 text-water" />
          )}
          <span>{it.mensaje}</span>
        </li>
      ))}
    </ul>
  );
}
