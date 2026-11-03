import { AlertTriangle, CheckCircle2, Clock3, Flag, Loader2, OctagonAlert } from 'lucide-react';
import type { MaintenancePriority, MaintenanceStatus } from '../../types/api';
import { cn } from '../../lib/cn';

const STATUS: Record<MaintenanceStatus, { label: string; cls: string; Icon: typeof Clock3 }> = {
  pendiente: { label: 'Pendiente', cls: 'border-warn/40 bg-warn-soft text-warn', Icon: Clock3 },
  en_proceso: {
    label: 'En proceso',
    cls: 'border-moss/40 bg-neutral-soft text-moss',
    Icon: Loader2,
  },
  finalizado: {
    label: 'Finalizada',
    cls: 'border-success/40 bg-success-soft text-success',
    Icon: CheckCircle2,
  },
};

const PRIORITY: Record<MaintenancePriority, { label: string; cls: string; Icon: typeof Flag }> = {
  alta: { label: 'Alta', cls: 'border-danger/40 bg-danger-soft text-danger', Icon: OctagonAlert },
  media: { label: 'Media', cls: 'border-warn/40 bg-warn-soft text-warn', Icon: Flag },
  baja: { label: 'Baja', cls: 'border-border bg-neutral-soft text-ink-2', Icon: Flag },
};

export function TaskStatusBadge({
  estado,
  vencida,
}: {
  estado: MaintenanceStatus;
  vencida: boolean;
}) {
  if (vencida && estado !== 'finalizado') {
    return (
      <span className="inline-flex items-center gap-1 rounded-[4px] border border-danger/40 bg-danger-soft px-1.5 py-0.5 text-[12px] font-semibold text-danger">
        <AlertTriangle size={13} strokeWidth={1.5} aria-hidden="true" />
        Vencida
      </span>
    );
  }
  const { label, cls, Icon } = STATUS[estado];
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-[4px] border px-1.5 py-0.5 text-[12px] font-semibold', cls)}>
      <Icon size={13} strokeWidth={1.5} aria-hidden="true" />
      {label}
    </span>
  );
}

export function TaskPriorityBadge({ prioridad }: { prioridad: MaintenancePriority }) {
  const { label, cls, Icon } = PRIORITY[prioridad];
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-[4px] border px-1.5 py-0.5 text-[11px] font-semibold', cls)}>
      <Icon size={12} strokeWidth={1.5} aria-hidden="true" />
      {label}
    </span>
  );
}
