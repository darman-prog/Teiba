import type { ParqueDetalle, ParqueListResponse } from '../types/api';
import { isMockEnabled, requestJson } from './client';
import { FIXTURE_PARQUES, fixtureParqueDetalle } from '../test/fixtures';
import { ApiError } from './errors';

// Índice del libro con timeout de 10 s.
export async function fetchParques(): Promise<{ data: ParqueListResponse; traceId: string | null }> {
  if (isMockEnabled()) {
    await new Promise((r) => setTimeout(r, 150));
    return { data: FIXTURE_PARQUES, traceId: 'demo-trace-parques' };
  }
  return requestJson<ParqueListResponse>('/api/parques', { timeoutMs: 10_000 });
}

// Ficha del libro; 404 si el código no existe.
export async function fetchParque(codigo: string): Promise<{ data: ParqueDetalle; traceId: string | null }> {
  if (isMockEnabled()) {
    await new Promise((r) => setTimeout(r, 150));
    const found = FIXTURE_PARQUES.items.some((p) => p.codigo === codigo);
    if (!found) throw new ApiError({ code: 'not_found', message: `No existe el parque '${codigo}'.`, status: 404 });
    return { data: fixtureParqueDetalle(codigo), traceId: 'demo-trace-parque' };
  }
  // El código viaja en el path; se codifica para evitar inyección.
  return requestJson<ParqueDetalle>(`/api/parques/${encodeURIComponent(codigo)}`, { timeoutMs: 10_000 });
}
