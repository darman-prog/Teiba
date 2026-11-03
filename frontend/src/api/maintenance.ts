import { requestJson } from './client';
import type {
  ElementoListResponse,
  IncidenteListResponse,
  MaintenanceCreateBody,
  MaintenanceEstadoBody,
  MaintenanceItem,
  MaintenanceListResponse,
  OperadorListResponse,
} from '../types/api';

function query(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : '';
}

export async function fetchMantenimientos(params: {
  estado?: string;
  prioridad?: string;
  parque?: string;
  limite?: number;
} = {}): Promise<MaintenanceListResponse> {
  const { data } = await requestJson<MaintenanceListResponse>(
    `/api/mantenimientos${query(params)}`,
    { timeoutMs: 10000 },
  );
  return data;
}

export async function fetchOperadores(): Promise<OperadorListResponse> {
  const { data } = await requestJson<OperadorListResponse>('/api/operadores', {
    timeoutMs: 8000,
  });
  return data;
}

export async function fetchIncidentes(parque: string): Promise<IncidenteListResponse> {
  const { data } = await requestJson<IncidenteListResponse>(
    `/api/incidentes${query({ parque })}`,
    { timeoutMs: 8000 },
  );
  return data;
}

export async function fetchElementos(parque: string): Promise<ElementoListResponse> {
  const { data } = await requestJson<ElementoListResponse>(
    `/api/elementos${query({ parque })}`,
    { timeoutMs: 8000 },
  );
  return data;
}

export async function createMantenimiento(
  body: MaintenanceCreateBody,
): Promise<MaintenanceItem> {
  const { data } = await requestJson<MaintenanceItem>('/api/mantenimientos', {
    method: 'POST',
    body,
    timeoutMs: 12000,
  });
  return data;
}

export async function changeMantenimientoEstado(
  id: string,
  body: MaintenanceEstadoBody,
): Promise<MaintenanceItem> {
  const { data } = await requestJson<MaintenanceItem>(
    `/api/mantenimientos/${encodeURIComponent(id)}/estado`,
    { method: 'PATCH', body, timeoutMs: 12000 },
  );
  return data;
}

export async function reassignMantenimiento(
  id: string,
  responsableId: string,
): Promise<MaintenanceItem> {
  const { data } = await requestJson<MaintenanceItem>(
    `/api/mantenimientos/${encodeURIComponent(id)}/responsable`,
    { method: 'PATCH', body: { responsable_id: responsableId }, timeoutMs: 12000 },
  );
  return data;
}

export async function changeIncidenteEstado(
  id: string,
  estado: string,
): Promise<IncidenteListResponse['items'][number]> {
  const { data } = await requestJson<IncidenteListResponse['items'][number]>(
    `/api/incidentes/${encodeURIComponent(id)}/estado`,
    { method: 'PATCH', body: { estado }, timeoutMs: 12000 },
  );
  return data;
}
