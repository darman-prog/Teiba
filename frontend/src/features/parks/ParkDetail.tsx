import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useParque } from '../../hooks/useParque';
import { ParkFacts } from './ParkFacts';
import { SectorList } from './SectorList';
import { IndicationList } from './IndicationList';
import { useDocumentTitle } from '../../lib/useDocumentTitle';

// Ficha del libro con sectores e indicaciones; 404 si el código no existe.
export function ParkDetail() {
  const { codigo } = useParams<{ codigo: string }>();
  const { data, loading, error } = useParque(codigo);
  useDocumentTitle(data?.nombre ? `${data.nombre} · Teiba` : 'Ficha de parque · Teiba');

  return (
    <div className="flex flex-col gap-3">
      <Link to="/parques" className="inline-flex min-h-[44px] w-fit items-center gap-1.5 rounded-[6px] px-2 text-[14px] font-semibold text-ink-2 hover:text-ink">
        <ArrowLeft size={16} strokeWidth={1.5} aria-hidden="true" />
        Volver al libro
      </Link>

      {loading ? (
        <div role="status" aria-label="Cargando ficha" className="flex flex-col gap-2">
          <div className="skeleton h-8 w-2/3 rounded-[6px]" aria-hidden="true" />
          <div className="skeleton h-24 rounded-[8px]" aria-hidden="true" />
          <span className="sr-only">Cargando ficha del parque…</span>
        </div>
      ) : error ? (
        <div role="alert" className="rounded-[8px] border border-danger/40 bg-danger-soft p-4">
          <p className="text-[15px] font-semibold text-danger">
            {error.code === 'not_found' ? `No existe el parque '${codigo}'.` : `No se pudo cargar la ficha: ${error.message}`}
          </p>
          {error.traceId && <p className="mt-1 font-mono text-[12px] text-ink">traceId: {error.traceId}</p>}
          <Link to="/parques" className="mt-3 inline-flex min-h-[44px] items-center rounded-[6px] bg-moss px-4 text-[14px] font-semibold text-white">
            Volver al índice
          </Link>
        </div>
      ) : !data ? (
        <div className="rounded-[8px] border border-dashed border-border bg-surface p-6 text-center">
          <p className="font-display text-[15px] font-semibold">Ficha vacía</p>
          <p className="text-[14px] text-ink-2">El servidor no devolvió contenido para este código.</p>
        </div>
      ) : (
        <article aria-labelledby="parque-nombre" className="flex flex-col gap-3 rounded-[8px] border border-border bg-surface p-4">
          <div>
            <p className="data-mono text-[12px] text-ink-2">{data.codigo}</p>
            <h1 id="parque-nombre" className="font-display text-[22px] font-semibold text-ink">
              {data.nombre}
            </h1>
          </div>
          <ParkFacts parque={data} />
          <div>
            <h2 className="field-label">Sectores ({data.sectores.length})</h2>
            <div className="mt-1.5">
              <SectorList sectores={data.sectores} />
            </div>
          </div>
          {data.indicaciones.length > 0 && (
            <div>
              <h2 className="field-label">Indicaciones de manejo</h2>
              <div className="mt-1.5">
                <IndicationList indicaciones={data.indicaciones} />
              </div>
            </div>
          )}
        </article>
      )}
    </div>
  );
}
