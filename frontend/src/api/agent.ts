import type { ConsultaResponse } from '../types/api';
import { isMockEnabled, newRequestId, requestJson } from './client';
import { FIXTURE_CONSULTA } from '../test/fixtures';

// Consulta al agente con timeout largo de 90 s; el backend orquesta tools + LLM.
export async function postConsulta(pregunta: string): Promise<{ data: ConsultaResponse; traceId: string | null }> {
  if (isMockEnabled()) {
    await new Promise((r) => setTimeout(r, 600));
    const q = pregunta.toLowerCase();
    // Variante sin reportar para cubrir el flujo de antena en demo.
    if (q.includes('ant-01') || q.includes('sin reportar')) {
      return {
        data: {
          ...FIXTURE_CONSULTA,
          respuesta:
            'La antena ANT-01 alimenta a SS-01, SS-02 y MET-01. SS-02 lleva 7 h sin reportar y MET-01 no tiene lecturas.',
          trazas: [
            {
              tool: 'get_devices_by_antenna',
              args: { antena: 'ANT-01' },
              ok: true,
              ms: 14,
              resumen: '3 hijos; 1 sin reportar, 1 sin datos',
              resultado: '{"antena": "ANT-01", "hijos": ["SS-01", "SS-02", "MET-01"]}',
            },
          ],
          meta: { ...FIXTURE_CONSULTA.meta, pasos: 2, trace_id: 'demo-trace-ant01' },
        },
        traceId: 'demo-trace-ant01',
      };
    }
    return { data: { ...FIXTURE_CONSULTA, meta: { ...FIXTURE_CONSULTA.meta, trace_id: `demo-${Date.now()}` } }, traceId: 'demo-trace-001' };
  }
  const requestId = newRequestId();
  const { data, traceId } = await requestJson<ConsultaResponse>('/api/agente/consulta', {
    method: 'POST',
    body: { pregunta },
    timeoutMs: 90_000,
    requestId,
  });
  return { data, traceId };
}
