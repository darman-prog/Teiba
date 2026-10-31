import { useMemo, useState } from 'react';
import { BookOpen, Loader2 } from 'lucide-react';
import { useParques } from '../../hooks/useParques';
import { ParkCard } from './ParkCard';
import { ParkFilters, type ParkFilterValue } from './ParkFilters';
import { SearchInput } from '../../shared/ui/SearchInput';
import { useDocumentTitle } from '../../lib/useDocumentTitle';

// Índice del libro: búsqueda + filtros, estados loading/error/empty.
export function ParkIndex() {
  const { items, loading, error, reload } = useParques();
  useDocumentTitle('Libro de parques · Teiba');
  const [q, setQ] = useState('');
  const [filters, setFilters] = useState<ParkFilterValue>({ comuna: '', tipo: '', estado: '' });

  const comunas = useMemo(() => [...new Set(items.map((p) => p.comuna).filter((v): v is string => !!v))].sort(), [items]);
  const tipos = useMemo(() => [...new Set(items.map((p) => p.tipo_parque).filter((v): v is string => !!v))].sort(), [items]);
  const estados = useMemo(() => [...new Set(items.map((p) => p.estado_general).filter((v): v is string => !!v))].sort(), [items]);

  // Búsqueda por nombre, código, comuna o dirección; filtros exactos.
  const visibles = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return items.filter((p) => {
      if (filters.comuna && p.comuna !== filters.comuna) return false;
      if (filters.tipo && p.tipo_parque !== filters.tipo) return false;
      if (filters.estado && p.estado_general !== filters.estado) return false;
      if (!needle) return true;
      return [p.nombre, p.codigo, p.comuna ?? '', p.direccion ?? ''].join(' ').toLowerCase().includes(needle);
    });
  }, [items, q, filters]);

  return (
    <div className="flex flex-col gap-3">
      <div>
        <h1 className="flex items-center gap-2 font-display text-[20px] font-semibold text-ink">
          <BookOpen size={19} strokeWidth={1.5} aria-hidden="true" className="text-moss" />
          Libro de parques
        </h1>
        <p className="text-[14px] text-ink-2">Catálogo de solo lectura para el rol usuario. Sin mapa ni telemetría en vivo.</p>
      </div>

      <div className="rounded-[8px] border border-border bg-surface p-3 md:p-4">
        <SearchInput id="buscar-parque" label="Buscar parque" value={q} onChange={setQ} placeholder="Nombre, código, comuna…" />
        <div className="mt-2">
          <ParkFilters value={filters} comunas={comunas} tipos={tipos} estados={estados} onChange={setFilters} />
        </div>
        <p className="mt-2 text-[12px] text-ink-2" role="status">
          {loading ? 'Cargando parques…' : `${visibles.length} de ${items.length} parques`}
        </p>
      </div>

      {loading ? (
        <div role="status" aria-label="Cargando parques" className="grid gap-2 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-[132px] rounded-[8px]" aria-hidden="true" />
          ))}
          <span className="sr-only">Cargando…</span>
          <Loader2 aria-hidden="true" className="hidden" />
        </div>
      ) : error ? (
        <div role="alert" className="rounded-[8px] border border-danger/40 bg-danger-soft p-4">
          <p className="text-[14px] font-semibold text-danger">No se pudo cargar el libro: {error.message}</p>
          {error.traceId && <p className="mt-1 font-mono text-[12px] text-ink">traceId: {error.traceId}</p>}
          <button type="button" onClick={reload} className="mt-2 min-h-[44px] rounded-[6px] bg-moss px-4 text-[14px] font-semibold text-white">
            Reintentar
          </button>
        </div>
      ) : visibles.length === 0 ? (
        <div className="rounded-[8px] border border-dashed border-border bg-surface p-6 text-center">
          <p className="font-display text-[15px] font-semibold">Sin resultados</p>
          <p className="mt-1 text-[14px] text-ink-2">Ajusta la búsqueda o limpia los filtros del libro.</p>
        </div>
      ) : (
        <div className="grid gap-2 sm:grid-cols-2">
          {visibles.map((p) => (
            <ParkCard key={p.codigo} parque={p} />
          ))}
        </div>
      )}
    </div>
  );
}
