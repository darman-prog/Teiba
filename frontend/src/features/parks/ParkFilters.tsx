import { FieldLabel } from '../../shared/ui/FieldLabel';

// Filtros del libro: comuna, tipo y estado con selects nativos accesibles.
export interface ParkFilterValue {
  comuna: string;
  tipo: string;
  estado: string;
}

export function ParkFilters({
  value,
  comunas,
  tipos,
  estados,
  onChange,
}: {
  value: ParkFilterValue;
  comunas: string[];
  tipos: string[];
  estados: string[];
  onChange: (v: ParkFilterValue) => void;
}) {
  const cls = 'rounded-[6px] border border-border bg-surface px-2.5 py-2 text-[14px] text-ink';
  return (
    <div className="grid gap-2 sm:grid-cols-3">
      <div className="flex flex-col gap-1">
        <FieldLabel htmlFor="f-comuna">Comuna</FieldLabel>
        <select id="f-comuna" value={value.comuna} onChange={(e) => onChange({ ...value, comuna: e.target.value })} className={cls}>
          <option value="">Todas</option>
          {comunas.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <FieldLabel htmlFor="f-tipo">Tipo</FieldLabel>
        <select id="f-tipo" value={value.tipo} onChange={(e) => onChange({ ...value, tipo: e.target.value })} className={cls}>
          <option value="">Todos</option>
          {tipos.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <FieldLabel htmlFor="f-estado">Estado</FieldLabel>
        <select id="f-estado" value={value.estado} onChange={(e) => onChange({ ...value, estado: e.target.value })} className={cls}>
          <option value="">Todos</option>
          {estados.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
