import { useCallback, useRef, useState } from 'react';
import { postConsulta } from '../api/agent';
import { ApiError } from '../api/errors';
import type { ConsultaResponse } from '../types/api';

export type Role = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: Role;
  texto: string;
  trazas: ConsultaResponse['trazas'];
  meta: ConsultaResponse['meta'] | null;
  traceId: string | null;
  failed?: boolean;
  failedPregunta?: string;
  errorCode?: string;
  errorMessage?: string;
  retryAfter?: string | null;
}

interface AgentState {
  messages: ChatMessage[];
  loading: boolean;
  error: ApiError | null;
  lastFailed: string | null;
  selectedId: string | null;
  send: (pregunta: string) => Promise<void>;
  retry: () => Promise<void>;
  dismissError: () => void;
  select: (id: string | null) => void;
  reset: () => void;
}

let seq = 0;
// Identificador local estable para claves de React y selección.
function nid(prefix: string): string {
  seq += 1;
  return `${prefix}-${Date.now()}-${seq}`;
}

// Bucle de bitácora: cada respuesta guarda sus trazas sin mezclar turnos.
export function useAgent(onAnswered?: () => void): AgentState {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [lastFailed, setLastFailed] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const busy = useRef(false);

  const run = useCallback(
    async (pregunta: string) => {
      // Evita doble envío mientras hay una consulta en vuelo.
      if (busy.current) return;
      busy.current = true;
      setLoading(true);
      setError(null);
      const userMsg: ChatMessage = { id: nid('u'), role: 'user', texto: pregunta, trazas: [], meta: null, traceId: null };
      setMessages((m) => [...m, userMsg]);
      try {
        const { data, traceId } = await postConsulta(pregunta);
        const asst: ChatMessage = {
          id: nid('a'),
          role: 'assistant',
          texto: data.respuesta,
          trazas: data.trazas,
          meta: data.meta,
          traceId: traceId ?? data.meta.trace_id,
        };
        setMessages((m) => [...m, asst]);
        setSelectedId(asst.id);
        setLastFailed(null);
        onAnswered?.();
      } catch (e: unknown) {
        const api = e instanceof ApiError ? e : new ApiError({ code: 'network', message: 'Sin conexión.', status: 0 });
        setError(api);
        setLastFailed(pregunta);
        const fail: ChatMessage = {
          id: nid('e'),
          role: 'assistant',
          texto: '',
          trazas: [],
          meta: null,
          traceId: api.traceId,
          failed: true,
          failedPregunta: pregunta,
          errorCode: api.code,
          errorMessage: api.message,
          retryAfter: api.retryAfter,
        };
        setMessages((m) => [...m, fail]);
        setSelectedId(fail.id);
      } finally {
        busy.current = false;
        setLoading(false);
      }
    },
    [onAnswered],
  );

  const send = useCallback(
    async (pregunta: string) => {
      const p = pregunta.trim();
      if (p.length < 3 || p.length > 500 || loading) return;
      await run(p);
    },
    [loading, run],
  );

  const retry = useCallback(async () => {
    if (lastFailed && !loading) await run(lastFailed);
  }, [lastFailed, loading, run]);

  const dismissError = useCallback(() => {
    setError(null);
    setLastFailed(null);
    // Retira la entrada de error sin borrar la conversación válida.
    setMessages((m) => m.filter((x) => !x.failed));
  }, []);

  const select = useCallback((id: string | null) => setSelectedId(id), []);

  const reset = useCallback(() => {
    setMessages([]);
    setError(null);
    setLastFailed(null);
    setSelectedId(null);
  }, []);

  return { messages, loading, error, lastFailed, selectedId, send, retry, dismissError, select, reset };
}
