import type { ReactNode } from 'react';

// Etiqueta de instrumento: Overpass 600, 12px, mayúsculas medidas.
export function FieldLabel({ htmlFor, children }: { htmlFor?: string; children: ReactNode }) {
  return (
    <label htmlFor={htmlFor} className="field-label">
      {children}
    </label>
  );
}
