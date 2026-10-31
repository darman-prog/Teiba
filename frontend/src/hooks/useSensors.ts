import { useCallback, useEffect, useState } from 'react';
import { fetchSensores } from '../api/sensors';
import { ApiError } from '../api/errors';
import type { SensorItem } from '../types/api';

interface SensorsState {
  items: SensorItem[];
  total: number;
  loading: boolean;
  error: ApiError | null;
  refresh: () => void;
}

// Transecto de sensores con reintento manual y refresh tras cada respuesta.
export function useSensors(): SensorsState {
  const [items, setItems] = useState<SensorItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchSensores(5)
      .then(({ data }) => {
        if (!alive) return;
        setItems(data.items);
        setTotal(data.total);
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

  const refresh = useCallback(() => setTick((t) => t + 1), []);
  return { items, total, loading, error, refresh };
}
