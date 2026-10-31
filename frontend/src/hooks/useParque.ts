import { useEffect, useState } from 'react';
import { fetchParque } from '../api/parks';
import { ApiError } from '../api/errors';
import type { ParqueDetalle } from '../types/api';

// Ficha del libro con estados loading/error/empty/404.
export function useParque(codigo: string | undefined) {
  const [data, setData] = useState<ParqueDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!codigo) {
      setLoading(false);
      return;
    }
    let alive = true;
    setLoading(true);
    fetchParque(codigo)
      .then(({ data: d }) => {
        if (!alive) return;
        setData(d);
        setError(null);
      })
      .catch((e: unknown) => {
        if (!alive) return;
        setError(e instanceof ApiError ? e : new ApiError({ code: 'network', message: 'Sin conexión.', status: 0 }));
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [codigo]);

  return { data, loading, error };
}
