import { Landmark, MapPin, Ruler } from 'lucide-react';
import type { ParqueDetalle } from '../../types/api';
import { formatArea } from '../../lib/format';

// Hechos de la ficha: comuna, dirección, área, tipo y estado.
export function ParkFacts({ parque }: { parque: ParqueDetalle }) {
  const rows = [
    { Icon: MapPin, label: 'Ubicación', value: [parque.comuna, parque.direccion].filter(Boolean).join(' · ') || '—' },
    { Icon: Ruler, label: 'Área', value: formatArea(parque.area_m2) },
    { Icon: Landmark, label: 'Tipo / estado', value: [parque.tipo_parque, parque.estado_general].filter(Boolean).join(' · ') || '—' },
  ];
  return (
    <dl className="grid gap-2 sm:grid-cols-3">
      {rows.map(({ Icon, label, value }) => (
        <div key={label} className="rounded-[6px] border border-border bg-mineral/50 px-3 py-2">
          <dt className="flex items-center gap-1.5 text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-2">
            <Icon size={13} strokeWidth={1.5} aria-hidden="true" />
            {label}
          </dt>
          <dd className="mt-0.5 text-[14px] font-medium text-ink">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
