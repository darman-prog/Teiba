import { useEffect, useState } from 'react';
import { ApiError } from '../../api/errors';
import {
  changeIncidenteEstado,
  changeMantenimientoEstado,
  fetchOperadores,
  reassignMantenimiento,
} from '../../api/maintenance';
import { formatFechaCorta } from '../../lib/format';
import type { IncidentStatus, MaintenanceItem, OperadorItem } from '../../types/api';
import { Button } from '../../shared/ui/Button';
import { TaskPriorityBadge, TaskStatusBadge } from './TaskBadge';

function mensaje(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.code === 'invalid_transition') return 'Ese cambio de estado no está permitido.';
    if (err.code === 'invalid_request') return err.message;
    if (err.code === 'forbidden') return 'No tienes permisos para esta acción.';
    return err.message;
  }
  return 'No se pudo completar la acción.';
}

const SIGUIENTE_INCIDENTE: Record<IncidentStatus, IncidentStatus[]> = {
  reportado: ['en_revision'],
  en_revision: ['en_proceso'],
  en_proceso: ['resuelto'],
  resuelto: ['en_proceso'],
};

const INCIDENTE_LABEL: Record<IncidentStatus, string> = {
  reportado: 'Reportado',
  en_revision: 'En revisión',
  en_proceso: 'En proceso',
  resuelto: 'Resuelto',
};

export function MaintenanceDetail({
  item,
  esAdmin,
  onChanged,
}: {
  item: MaintenanceItem;
  esAdmin: boolean;
  onChanged: () => void;
}) {
  const [nota, setNota] = useState('');
  const [operadores, setOperadores] = useState<OperadorItem[]>([]);
  const [reasignarId, setReasignarId] = useState(item.responsable?.id ?? '');
  const [incidenteDestino, setIncidenteDestino] = useState<IncidentStatus | ''>('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (!esAdmin) return;
    let alive = true;
    fetchOperadores()
      .then((data) => {
        if (alive) setOperadores(data.items);
      })
      .catch(() => {
        /* el detalle sigue visible si falla el catálogo */
      });
    return () => {
      alive = false;
    };
  }, [esAdmin]);

  useEffect(() => {
    setReasignarId(item.responsable?.id ?? '');
    setIncidenteDestino('');
    setNota('');
    setError(null);
  }, [item.id]);

  async function cambiar(estado: 'en_proceso' | 'finalizado') {
    if (enviando) return;
    const requiereNota = estado === 'finalizado' || item.estado === 'finalizado';
    if (requiereNota && !nota.trim()) {
      setError('Escribe una nota antes de continuar.');
      return;
    }
    setError(null);
    setEnviando(true);
    try {
      await changeMantenimientoEstado(item.id, {
        estado,
        nota: nota.trim() || null,
      });
      setNota('');
      onChanged();
    } catch (err) {
      setError(mensaje(err));
    } finally {
      setEnviando(false);
    }
  }

  async function reasignar() {
    if (!reasignarId || enviando) return;
    setError(null);
    setEnviando(true);
    try {
      await reassignMantenimiento(item.id, reasignarId);
      onChanged();
    } catch (err) {
      setError(mensaje(err));
    } finally {
      setEnviando(false);
    }
  }

  async function actualizarIncidente() {
    if (!item.incidente || !incidenteDestino || enviando) return;
    setError(null);
    setEnviando(true);
    try {
      await changeIncidenteEstado(item.incidente.id, incidenteDestino);
      setIncidenteDestino('');
      onChanged();
    } catch (err) {
      setError(mensaje(err));
    } finally {
      setEnviando(false);
    }
  }

  const abierta = item.estado === 'pendiente' || item.estado === 'en_proceso';
  const puedeFinalizar = esAdmin ? abierta : item.estado === 'en_proceso';
  const puedeReabrir = esAdmin && item.estado === 'finalizado';
  const puedeIniciar = !esAdmin && item.estado === 'pendiente';
  const puedeReasignar = esAdmin && abierta;
  const notaRequerida = item.estado === 'finalizado' ? puedeReabrir : puedeFinalizar;

  return (
    <section aria-labelledby="detalle-tarea" className="rounded-[8px] border border-border bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="field-label">Detalle de la tarea</p>
          <h2 id="detalle-tarea" className="mt-1 font-display text-[17px] font-semibold text-ink">
            {item.descripcion}
          </h2>
        </div>
        <TaskStatusBadge estado={item.estado} vencida={item.vencida} />
      </div>

      <div className="mt-2 flex flex-wrap items-center gap-2 text-[12px] text-ink-2">
        <TaskPriorityBadge prioridad={item.prioridad} />
        <span className="data-mono">{item.tipo}</span>
        {item.parque && <span>{item.parque.nombre}</span>}
        {item.responsable && <span>· {item.responsable.nombre}</span>}
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-2 text-[13px]">
        <div>
          <dt className="field-label">Programada</dt>
          <dd className="data-mono">{formatFechaCorta(item.fecha_programada)}</dd>
        </div>
        <div>
          <dt className="field-label">Ejecución</dt>
          <dd className="data-mono">{formatFechaCorta(item.fecha_ejecucion)}</dd>
        </div>
        {item.costo_estimado != null && (
          <div>
            <dt className="field-label">Costo estimado</dt>
            <dd className="data-mono">
              {new Intl.NumberFormat('es-CO').format(item.costo_estimado)} COP
            </dd>
          </div>
        )}
        {item.fecha_reapertura && (
          <div>
            <dt className="field-label">Reabierta</dt>
            <dd className="data-mono">{formatFechaCorta(item.fecha_reapertura)}</dd>
          </div>
        )}
      </dl>

      {item.elemento && (
        <p className="mt-2 text-[13px] text-ink-2">
          Elemento: {item.elemento.tipo_elemento ?? '—'} ({item.elemento.cantidad ?? '—'})
        </p>
      )}

      {item.incidente && (
        <div className="mt-3 rounded-[6px] border border-border bg-mineral/40 p-3">
          <p className="field-label">Incidente vinculado</p>
          <p className="mt-1 text-[13px] text-ink">
            {item.incidente.tipo ?? 'Incidente'} · {item.incidente.descripcion}
          </p>
          <p className="mt-1 text-[12px] text-ink-2">
            Estado: <span className="font-semibold">{item.incidente.estado}</span>
          </p>
          {esAdmin && item.incidente.estado && (
            <div className="mt-2 flex flex-wrap items-end gap-2">
              <label htmlFor="incidente-destino" className="field-label">
                Cambiar a
              </label>
              <select
                id="incidente-destino"
                value={incidenteDestino}
                onChange={(e) => setIncidenteDestino(e.target.value as IncidentStatus)}
                className="rounded-[6px] border border-border bg-surface px-2 py-1.5 text-[13px]"
              >
                <option value="">Elige estado</option>
                {SIGUIENTE_INCIDENTE[item.incidente.estado].map((estado) => (
                  <option key={estado} value={estado}>
                    {INCIDENTE_LABEL[estado]}
                  </option>
                ))}
              </select>
              <Button
                variant="secondary"
                type="button"
                onClick={actualizarIncidente}
                disabled={!incidenteDestino || enviando}
              >
                Actualizar incidente
              </Button>
            </div>
          )}
        </div>
      )}

      {item.nota_cierre && (
        <p className="mt-3 text-[13px] text-ink">
          <span className="field-label">Cierre:</span> {item.nota_cierre}
        </p>
      )}
      {item.nota_reapertura && (
        <p className="mt-1 text-[13px] text-ink">
          <span className="field-label">Reapertura:</span> {item.nota_reapertura}
        </p>
      )}

      {(puedeFinalizar || puedeReabrir) && (
        <div className="mt-3 flex flex-col gap-1">
          <label htmlFor="nota-tarea" className="field-label">
            {puedeReabrir ? 'Nota de reapertura' : 'Nota de cierre'}
          </label>
          <textarea
            id="nota-tarea"
            rows={2}
            maxLength={300}
            value={nota}
            onChange={(e) => setNota(e.target.value)}
            className="rounded-[6px] border border-border bg-surface px-2.5 py-2 text-[14px]"
            placeholder={puedeReabrir ? 'Explica por qué se reabre' : 'Describe el trabajo realizado'}
          />
        </div>
      )}

      {error && (
        <p role="alert" className="mt-3 rounded-[6px] border border-danger/40 bg-danger-soft px-3 py-2 text-[13px] text-danger">
          {error}
        </p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {puedeIniciar && (
          <Button type="button" onClick={() => cambiar('en_proceso')} disabled={enviando}>
            Iniciar tarea
          </Button>
        )}
        {puedeFinalizar && (
          <Button
            type="button"
            onClick={() => cambiar('finalizado')}
            disabled={enviando || (notaRequerida && !nota.trim())}
          >
            Finalizar tarea
          </Button>
        )}
        {puedeReabrir && (
          <Button
            type="button"
            variant="secondary"
            onClick={() => cambiar('en_proceso')}
            disabled={enviando || !nota.trim()}
          >
            Reabrir tarea
          </Button>
        )}
      </div>

      {puedeReasignar && (
        <div className="mt-3 flex flex-wrap items-end gap-2 border-t border-border pt-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="reasignar-operador" className="field-label">
              Reasignar a
            </label>
            <select
              id="reasignar-operador"
              value={reasignarId}
              onChange={(e) => setReasignarId(e.target.value)}
              className="rounded-[6px] border border-border bg-surface px-2 py-1.5 text-[13px]"
            >
              {operadores.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.nombre}
                </option>
              ))}
            </select>
          </div>
          <Button
            type="button"
            variant="secondary"
            onClick={reasignar}
            disabled={!reasignarId || enviando}
          >
            Reasignar
          </Button>
        </div>
      )}
    </section>
  );
}
