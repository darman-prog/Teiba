import { AlertTriangle, CheckCircle2, MinusCircle, OctagonAlert } from 'lucide-react';
import type { SensorEstado } from '../../types/api';
import { cn } from '../../lib/cn';

const MAP: Record<SensorEstado, { label: string; cls: string; Icon: typeof CheckCircle2 }> = {
  // ok usa success; warning usa tokens warn; danger usa danger; sin_datos es neutro.
  ok: { label: 'En rango', cls: 'border-success/40 bg-success-soft text-success', Icon: CheckCircle2 },
  warning: { label: 'Revisar', cls: 'border-warn/40 bg-warn-soft text-warn', Icon: AlertTriangle },
  danger: { label: 'Fuera de rango', cls: 'border-danger/40 bg-danger-soft text-danger', Icon: OctagonAlert },
  sin_datos: { label: 'Sin datos', cls: 'border-border bg-neutral-soft text-ink-2', Icon: MinusCircle },
};

// Estado con icono + texto, nunca solo color (WCAG).
export function StatusTag({ estado, size = 'sm' }: { estado: SensorEstado; size?: 'sm' | 'md' }) {
  const { label, cls, Icon } = MAP[estado];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-[4px] border font-semibold',
        size === 'sm' ? 'px-1.5 py-0.5 text-[12px]' : 'px-2 py-1 text-[13px]',
        cls,
      )}
    >
      <Icon size={size === 'sm' ? 13 : 15} strokeWidth={1.5} aria-hidden="true" />
      {label}
    </span>
  );
}
