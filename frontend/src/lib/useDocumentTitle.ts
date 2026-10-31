import { useEffect } from 'react';

// Título por ruta: WCAG 2.4.2 y contexto para pestañas/lectores.
export function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = title;
  }, [title]);
}
