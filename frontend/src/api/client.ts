import { ApiError, parseErrorBody } from './errors';

// Base de la API: en desarrollo el proxy de Vite sirve /api en el mismo origen.
export function apiBase(): string {
  const v = import.meta.env.VITE_API_URL as string | undefined;
  if (v && v.trim().length > 0) return v.replace(/\/$/, '');
  return '';
}

// Bandera de modo demo: fixtures idénticas al contrato, sin red.
export function isMockEnabled(): boolean {
  return String(import.meta.env.VITE_USE_MOCKS ?? 'false').toLowerCase() === 'true';
}

interface RequestOpts {
  timeoutMs: number;
  requestId?: string;
}

// fetch con timeout abortable; mapea errores de red y del contrato.
export async function requestJson<T>(path: string, opts: RequestOpts & { method?: string; body?: unknown }): Promise<{ data: T; traceId: string | null }> {
  const ctrl = new AbortController();
  // Guarda el temporizador para cancelarlo al terminar.
  const t = window.setTimeout(() => ctrl.abort(), opts.timeoutMs);
  try {
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (opts.body !== undefined) headers['Content-Type'] = 'application/json';
    if (opts.requestId) headers['X-Request-Id'] = opts.requestId;
    const res = await fetch(`${apiBase()}${path}`, {
      method: opts.method ?? 'GET',
      headers,
      // La sesión viaja en cookie httpOnly; el proxy same-origin la conserva.
      credentials: 'include',
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
      signal: ctrl.signal,
    });
    const traceId = res.headers.get('X-Trace-Id');
    let json: unknown = null;
    try {
      json = await res.json();
    } catch {
      json = null;
    }
    if (!res.ok) {
      // Un 401 fuera del login invalida la sesión y avisa a AuthProvider.
      if (res.status === 401 && path !== '/api/auth/login' && typeof window !== 'undefined') {
        window.dispatchEvent(new Event('teiba:unauthorized'));
      }
      const parsed = parseErrorBody(json);
      // 429 conserva Retry-After para el mensaje de espera.
      const retryAfter = res.status === 429 ? res.headers.get('Retry-After') : null;
      throw new ApiError({
        code: parsed?.code ?? (res.status === 429 ? 'rate_limited' : 'unknown'),
        message: parsed?.message ?? `Error ${res.status}`,
        status: res.status,
        traceId: parsed?.traceId ?? traceId,
        retryAfter,
        details: parsed?.details,
      });
    }
    return { data: json as T, traceId };
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError({ code: 'timeout', message: 'La consulta superó el tiempo máximo.', status: 504 });
    }
    throw new ApiError({ code: 'network', message: 'Sin conexión con la API.', status: 0 });
  } finally {
    window.clearTimeout(t);
  }
}

// Genera un X-Request-Id trazable sin dependencias.
export function newRequestId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
  return `req-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
}
