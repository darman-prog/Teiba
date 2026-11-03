import { useMemo, useState } from 'react';
import { ClipboardList, Plus, RefreshCw } from 'lucide-react';
import { useAuth } from '../../app/AuthProvider';
import { useMantenimientos } from '../../hooks/useMantenimientos';
import { formatFechaCorta } from '../../lib/format';
import type { MaintenanceItem, MaintenancePriority, MaintenanceStatus } from '../../types/api';
import { Button } from '../../shared/ui/Button';
import { MaintenanceDetail } from './MaintenanceDetail';
import { MaintenanceForm } from './MaintenanceForm';
import { TaskPriorityBadge, TaskStatusBadge } from './TaskBadge';

type FiltroEstado = MaintenanceStatus | '';
type FiltroPrioridad = MaintenancePriority | '';

export function MaintenanceView() {
  const { usuario, perfil } = useAuth();
  const { items, loading, error, reload } = useMantenimientos();
  const [filtroEstado, setFiltroEstado] = useState<FiltroEstado>('');
  const [filtroPrioridad, setFiltroPrioridad] = useState<FiltroPrioridad>('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mostrarForm, setMostrarForm] = useState(false);

  const esAdmin =
    usuario?.rol === 'admin' &&
    (perfil?.rol === 'administrador' || perfil?.rol === 'operador_mantenimiento');
  const esOperador = usuario?.rol === 'operator' && perfil?.rol === 'operador_mantenimiento';

  const visibles = useMemo(() => {
    return items.filter((item) => {
      if (filtroEstado && item.estado !== filtroEstado) return false;
      if (filtroPrioridad && item.prioridad !== filtroPrioridad) return false;
      return true;
    });
  }, [items, filtroEstado, filtroPrioridad]);

  const selected = items.find((item) => item.id === selectedId) ?? null;

  function creada(item: MaintenanceItem) {
    setMostrarForm(false);
    setSelectedId(item.id);
    reload();
  }

  if (!esAdmin && !esOperador) {
    return (
      <section className="rounded-[8px] border border-border bg-surface p-5">
        <h1 className="font-display text-[20px] font-semibold text-ink">Mantenimientos</h1>
        <p className="mt-2 text-[14px] text-ink-2">
          Tu perfil no tiene acceso a la vista de mantenimientos.
        </p>
      </section>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="flex items-center gap-2 font-display text-[20px] font-semibold text-ink">
            <ClipboardList size={19} strokeWidth={1.5} aria-hidden="true" className="text-moss" />
            {esAdmin ? 'Mantenimientos' : 'Mis tareas'}
          </h1>
          <p className="text-[14px] text-ink-2">
            {esAdmin
              ? 'Asigna tareas, controla el avance y cierra o reabre casos.'
              : 'Tareas asignadas a tu perfil; inicia y finaliza con una nota.'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {esAdmin && (
            <Button type="button" onClick={() => setMostrarForm((value) => !value)}>
              <Plus size={15} strokeWidth={1.5} aria-hidden="true" />
              {mostrarForm ? 'Cerrar formulario' : 'Asignar tarea'}
            </Button>
          )}
          <Button type="button" variant="secondary" onClick={reload}>
            <RefreshCw size={15} strokeWidth={1.5} aria-hidden="true" />
            Actualizar
          </Button>
        </div>
      </div>

      {mostrarForm && esAdmin && (
        <MaintenanceForm onCreated={creada} onCancel={() => setMostrarForm(false)} />
      )}

      <div className="flex flex-wrap items-end gap-2 rounded-[6px] border border-border bg-surface p-3">
        <div className="flex flex-col gap-1">
          <label htmlFor="filtro-estado" className="field-label">
            Estado
          </label>
          <select
            id="filtro-estado"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value as FiltroEstado)}
            className="rounded-[6px] border border-border bg-surface px-2.5 py-1.5 text-[13px]"
          >
            <option value="">Todos</option>
            <option value="pendiente">Pendiente</option>
            <option value="en_proceso">En proceso</option>
            <option value="finalizado">Finalizada</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="filtro-prioridad" className="field-label">
            Prioridad
          </label>
          <select
            id="filtro-prioridad"
            value={filtroPrioridad}
            onChange={(e) => setFiltroPrioridad(e.target.value as FiltroPrioridad)}
            className="rounded-[6px] border border-border bg-surface px-2.5 py-1.5 text-[13px]"
          >
            <option value="">Todas</option>
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
        </div>
        <p role="status" className="ml-auto text-[12px] text-ink-2">
          {loading ? 'Cargando tareas…' : `${visibles.length} de ${items.length} tareas`}
        </p>
      </div>

      {error && (
        <p role="alert" className="rounded-[6px] border border-danger/40 bg-danger-soft px-3 py-2 text-[13px] text-danger">
          No se pudieron cargar las tareas: {error.message}
          {error.traceId && <span className="ml-1 font-mono text-[11px]">traceId: {error.traceId}</span>}
        </p>
      )}

      <div className="grid items-start gap-3 xl:grid-cols-[minmax(0,1fr)_420px]">
        <section aria-label="Lista de tareas" className="rounded-[8px] border border-border bg-surface">
          {loading ? (
            <p className="p-4 text-[14px] text-ink-2">Cargando tareas…</p>
          ) : visibles.length === 0 ? (
            <p className="p-4 text-[14px] text-ink-2">
              No hay tareas para este filtro. {esAdmin ? 'Asigna una tarea o ajusta los filtros.' : 'Revisa más tarde.'}
            </p>
          ) : (
            <ul role="list" className="divide-y divide-border">
              {visibles.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    aria-pressed={selectedId === item.id}
                    onClick={() => setSelectedId(item.id)}
                    className={`flex w-full flex-col gap-1 px-4 py-3 text-left transition-colors hover:bg-neutral-soft ${
                      selectedId === item.id ? 'border-l-[3px] border-moss bg-neutral-soft' : ''
                    }`}
                  >
                    <span className="flex flex-wrap items-center gap-2">
                      <TaskStatusBadge estado={item.estado} vencida={item.vencida} />
                      <TaskPriorityBadge prioridad={item.prioridad} />
                      <span className="data-mono text-[11px] text-ink-2">{item.tipo}</span>
                    </span>
                    <span className="text-[14px] font-semibold text-ink">{item.descripcion}</span>
                    <span className="flex flex-wrap gap-x-3 gap-y-1 text-[12px] text-ink-2">
                      <span>{item.parque?.nombre ?? 'Sin parque'}</span>
                      {item.responsable && <span>· {item.responsable.nombre}</span>}
                      <span className="data-mono">· {formatFechaCorta(item.fecha_programada)}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <div>
          {selected ? (
            <MaintenanceDetail item={selected} esAdmin={esAdmin} onChanged={reload} />
          ) : (
            <div className="rounded-[8px] border border-dashed border-border bg-surface p-4">
              <p className="field-label">Detalle</p>
              <p className="mt-1 text-[14px] text-ink-2">
                Selecciona una tarea de la lista para ver sus notas, vínculos y acciones.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
