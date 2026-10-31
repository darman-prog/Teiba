import type { SensorListResponse } from '../types/api';
import { isMockEnabled, requestJson } from './client';
import { FIXTURE_SENSORS } from '../test/fixtures';

// Tira de sensores de suelo con timeout de 10 s.
export async function fetchSensores(limite = 5): Promise<{ data: SensorListResponse; traceId: string | null }> {
  if (isMockEnabled()) {
    await new Promise((r) => setTimeout(r, 150));
    return { data: FIXTURE_SENSORS, traceId: 'demo-trace-sensores' };
  }
  const q = new URLSearchParams({ tipo: 'calidad_suelo', limite: String(limite) });
  return requestJson<SensorListResponse>(`/api/sensores?${q.toString()}`, { timeoutMs: 10_000 });
}
