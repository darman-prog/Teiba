import { useCallback, useEffect, useState } from 'react';
import { fetchMantenimientos } from '../api/maintenance';
import { ApiError } from '../api/errors';
import type { MaintenanceItem } from '../types/api';

// Lista de tareas: el backend ya limita al operador a las suyas.
export function useMantenimientos() {
  const [items, setItems] = useState<MaintenanceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [tick, setTick] = useState(0);

  const reload = useCallback(() => setTick((value) => value + 1), []);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchMantenimientos()
      .then((data) => {
        if (!alive) return;
        setItems(data.items);
        setError(null);
      })
      .catch((err: unknown) => {
        if (!alive) return;
        setError(
          err instanceof ApiError
            ? err
            : new ApiError({ code: 'network', message: 'Sin conexión.', status: 0 }),
        );
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [tick]);

  return { items, loading, error, reload };
}
