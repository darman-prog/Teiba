import type { HealthResponse } from '../types/api';
import { isMockEnabled, requestJson } from './client';
import { FIXTURE_HEALTH } from '../test/fixtures';

// Salud del backend con timeout corto de 10 s.
export async function fetchHealth(): Promise<{ data: HealthResponse; traceId: string | null }> {
  if (isMockEnabled()) {
    await new Promise((r) => setTimeout(r, 120));
    return { data: FIXTURE_HEALTH, traceId: 'demo-trace-health' };
  }
  return requestJson<HealthResponse>('/api/health', { timeoutMs: 10_000 });
}
