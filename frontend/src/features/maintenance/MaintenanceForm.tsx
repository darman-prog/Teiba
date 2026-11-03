import { useEffect, useState, type FormEvent } from 'react';
import { ApiError } from '../../api/errors';
import {
  createMantenimiento,
  fetchElementos,
  fetchIncidentes,
  fetchOperadores,
} from '../../api/maintenance';
import { useParques } from '../../hooks/useParques';
import type {
  ElementoItem,
  IncidenteItem,
  MaintenanceItem,
  MaintenancePriority,
  OperadorItem,
} from '../../types/api';
import { Button } from '../../shared/ui/Button';

function fechaSugerida(): string {
  // datetime-local espera hora local sin zona; se envía como ISO al backend.
  const d = new Date(Date.now() + 24 * 60 * 60 * 1000);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T09:00`;
}

function mensaje(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  return 'No se pudo asignar la tarea.';
}

export function MaintenanceForm({
  onCreated,
  onCancel,
}: {
  onCreated: (item: MaintenanceItem) => void;
  onCancel: () => void;
}) {
  const { items: parques, loading: cargandoParques } = useParques();
  const [operadores, setOperadores] = useState<OperadorItem[]>([]);
  const [incidentes, setIncidentes] = useState<IncidenteItem[]>([]);
  const [elementos, setElementos] = useState<ElementoItem[]>([]);
  const [parque, setParque] = useState('');
  const [tipo, setTipo] = useState<'preventivo' | 'correctivo'>('correctivo');
  const [descripcion, setDescripcion] = useState('');
  const [fecha, setFecha] = useState(fechaSugerida);
  const [prioridad, setPrioridad] = useState<MaintenancePriority>('media');
  const [responsable, setResponsable] = useState('');
  const [incidente, setIncidente] = useState('');
  const [elemento, setElemento] = useState('');
  const [costo, setCosto] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    let alive = true;
    fetchOperadores()
      .then((data) => {
        if (alive) setOperadores(data.items);
      })
      .catch((err: unknown) => {
        if (alive) setError(mensaje(err));
      });
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    if (!parque) {
      setIncidentes([]);
      setElementos([]);
      return;
    }
    let alive = true;
    Promise.all([fetchIncidentes(parque), fetchElementos(parque)])
      .then(([inc, ele]) => {
        if (!alive) return;
        setIncidentes(inc.items.filter((item) => item.estado !== 'resuelto'));
        setElementos(ele.items);
      })
      .catch((err: unknown) => {
        if (alive) setError(mensaje(err));
      });
    return () => {
      alive = false;
    };
  }, [parque]);

  async function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (enviando) return;
    setError(null);

    const fechaIso = new Date(fecha);
    if (Number.isNaN(fechaIso.getTime())) {
      setError('La fecha programada no es válida.');
      return;
    }
    if (!parque || !responsable || descripcion.trim().length < 3) {
      setError('Completa parque, descripción y responsable.');
      return;
    }

    setEnviando(true);
    try {
      const creada = await createMantenimiento({
        tipo,
        descripcion: descripcion.trim(),
        fecha_programada: fechaIso.toISOString(),
        prioridad,
        parque_codigo: parque,
        responsable_id: responsable,
        incidente_id: incidente || null,
        elemento_id: elemento || null,
        costo_estimado: costo.trim() ? Number(costo) : null,
      });
      onCreated(creada);
    } catch (err) {
      setError(mensaje(err));
    } finally {
      setEnviando(false);
    }
  }

  const campo = 'rounded-[6px] border border-border bg-surface px-2.5 py-2 text-[14px] text-ink';

  return (
    <form onSubmit={enviar} className="rounded-[8px] border border-border bg-surface p-4">
      <p className="field-label">Nueva tarea</p>
      <div className="mt-2 grid gap-3 md:grid-cols-2">
        <div className="flex flex-col gap-1">
          <label htmlFor="mt-parque" className="field-label">
            Parque
          </label>
          <select
            id="mt-parque"
            value={parque}
            onChange={(e) => {
              setParque(e.target.value);
              setIncidente('');
              setElemento('');
            }}
            className={campo}
            required
          >
            <option value="">{cargandoParques ? 'Cargando…' : 'Elige un parque'}</option>
            {parques.map((p) => (
              <option key={p.codigo} value={p.codigo}>
                {p.codigo} — {p.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-responsable" className="field-label">
            Operador
          </label>
          <select
            id="mt-responsable"
            value={responsable}
            onChange={(e) => setResponsable(e.target.value)}
            className={campo}
            required
          >
            <option value="">Elige un operador</option>
            {operadores.map((o) => (
              <option key={o.id} value={o.id}>
                {o.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-tipo" className="field-label">
            Tipo
          </label>
          <select
            id="mt-tipo"
            value={tipo}
            onChange={(e) => setTipo(e.target.value as 'preventivo' | 'correctivo')}
            className={campo}
          >
            <option value="correctivo">Correctivo</option>
            <option value="preventivo">Preventivo</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-fecha" className="field-label">
            Fecha programada
          </label>
          <input
            id="mt-fecha"
            type="datetime-local"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            className={campo}
            required
          />
        </div>

        <div className="flex flex-col gap-1 md:col-span-2">
          <label htmlFor="mt-descripcion" className="field-label">
            Descripción
          </label>
          <textarea
            id="mt-descripcion"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            maxLength={250}
            rows={2}
            className={campo}
            required
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-prioridad" className="field-label">
            Prioridad
          </label>
          <select
            id="mt-prioridad"
            value={prioridad}
            onChange={(e) => setPrioridad(e.target.value as MaintenancePriority)}
            className={campo}
          >
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-costo" className="field-label">
            Costo estimado (COP)
          </label>
          <input
            id="mt-costo"
            type="number"
            min={0}
            value={costo}
            onChange={(e) => setCosto(e.target.value)}
            className={campo}
            placeholder="Opcional"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-incidente" className="field-label">
            Incidente vinculado
          </label>
          <select
            id="mt-incidente"
            value={incidente}
            onChange={(e) => {
              setIncidente(e.target.value);
              const item = incidentes.find((i) => i.id === e.target.value);
              if (item?.prioridad) setPrioridad(item.prioridad as MaintenancePriority);
            }}
            className={campo}
          >
            <option value="">Sin incidente</option>
            {incidentes.map((i) => (
              <option key={i.id} value={i.id}>
                {i.tipo ?? 'Incidente'} — {i.descripcion?.slice(0, 48)}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="mt-elemento" className="field-label">
            Elemento de inventario
          </label>
          <select
            id="mt-elemento"
            value={elemento}
            onChange={(e) => setElemento(e.target.value)}
            className={campo}
          >
            <option value="">Sin elemento</option>
            {elementos.map((e) => (
              <option key={e.id} value={e.id}>
                {e.tipo_elemento ?? 'Elemento'} ({e.cantidad ?? '—'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <p role="alert" className="mt-3 rounded-[6px] border border-danger/40 bg-danger-soft px-3 py-2 text-[13px] text-danger">
          {error}
        </p>
      )}

      <div className="mt-3 flex flex-wrap gap-2">
        <Button type="submit" disabled={enviando}>
          {enviando ? 'Asignando…' : 'Asignar tarea'}
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    </form>
  );
}
