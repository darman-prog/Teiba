import { useState } from 'react';
import { Button } from '../../shared/ui/Button';
import { Chip } from '../../shared/ui/Chip';
import { SearchInput } from '../../shared/ui/SearchInput';
import { Surface } from '../../shared/ui/Surface';
import { StatusTag } from '../sensors/StatusTag';
import { EmptyState } from '../agent/EmptyState';
import { LoadingState } from '../agent/LoadingState';
import { useDocumentTitle } from '../../lib/useDocumentTitle';

// Galería dev-only: una especie por primitiva, con sus estados.
export function Showcase() {
  const [q, setQ] = useState('');
  useDocumentTitle('Showcase · Teiba');

  return (
    <div className="flex flex-col gap-3">
      <header>
        <p className="field-label">Sistema de estación</p>
        <h1 className="font-display text-[20px] font-semibold text-ink">Especies de componentes</h1>
        <p className="mt-1 max-w-prose text-[13px] text-ink-2">
          Catálogo de primitivas de “Estación de campo”. Si una pantalla necesita otra especie, primero entra aquí y en DESIGN.md.
        </p>
      </header>

      <Surface className="p-3">
        <p className="field-label">Superficie</p>
        <p className="mt-1 text-[14px] text-ink">Surface: borde 1px, radio 8px, sin sombra.</p>
      </Surface>

      <section aria-labelledby="showcase-actions" className="rounded-[8px] border border-border bg-surface p-3">
        <p id="showcase-actions" className="field-label">Acciones</p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>

      <section aria-labelledby="showcase-tags" className="rounded-[8px] border border-border bg-surface p-3">
        <p id="showcase-tags" className="field-label">Etiquetas y estados</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Chip>Instrumento</Chip>
          <StatusTag estado="ok" />
          <StatusTag estado="warning" />
          <StatusTag estado="danger" />
          <StatusTag estado="sin_datos" />
        </div>
      </section>

      <section aria-labelledby="showcase-fields" className="rounded-[8px] border border-border bg-surface p-3">
        <p id="showcase-fields" className="field-label">Campos</p>
        <div className="mt-2">
          <SearchInput id="showcase-q" label="Búsqueda" value={q} onChange={setQ} placeholder="Filtrar el libro" />
        </div>
      </section>

      <section aria-labelledby="showcase-states">
        <p id="showcase-states" className="field-label">Estados</p>
        <div className="mt-2 grid gap-3 md:grid-cols-2">
          <EmptyState onPick={() => {}} />
          <LoadingState />
        </div>
      </section>
    </div>
  );
}
