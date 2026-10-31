import type { ApiErrorBody } from '../types/api';

// Error tipado del contrato: conserva code, message, traceId y Retry-After.
export class ApiError extends Error {
  code: string;
  status: number;
  traceId: string | null;
  retryAfter: string | null;
  details: unknown;

  constructor(opts: {
    code: string;
    message: string;
    status: number;
    traceId?: string | null;
    retryAfter?: string | null;
    details?: unknown;
  }) {
    super(opts.message);
    this.name = 'ApiError';
    this.code = opts.code;
    this.status = opts.status;
    this.traceId = opts.traceId ?? null;
    this.retryAfter = opts.retryAfter ?? null;
    this.details = opts.details;
  }
}

// Extrae el cuerpo de error del contrato sin asumir forma.
export function parseErrorBody(json: unknown): ApiErrorBody | null {
  if (!json || typeof json !== 'object') return null;
  const b = json as Record<string, unknown>;
  if (typeof b['code'] !== 'string' || typeof b['message'] !== 'string') return null;
  return {
    code: b['code'] as string,
    message: b['message'] as string,
    details: b['details'],
    traceId: typeof b['traceId'] === 'string' ? (b['traceId'] as string) : undefined,
  };
}
