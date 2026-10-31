import { useEffect, useState } from 'react';
import { fetchParques } from '../api/parks';
import { ApiError } from '../api/errors';
import type { ParqueResumen } from '../types/api';

// Índice del libro para el rol usuario (y admin que lo visita).
export function useParques() {
  const [items, setItems] = useState<ParqueResumen[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchParques()
      .then(({ data }) => {
        if (!alive) return;
        setItems(data.items);
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
  }, [tick]);

  return { items, loading, error, reload: () => setTick((t) => t + 1) };
}
