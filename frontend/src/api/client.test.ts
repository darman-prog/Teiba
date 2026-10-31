import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { ApiError, parseErrorBody } from './errors';
import { requestJson } from './client';

// Contraseña del parseo: el contrato trae {code,message,details,traceId}.
describe('parseErrorBody', () => {
  it('acepta el cuerpo válido del contrato', () => {
    expect(parseErrorBody({ code: 'not_found', message: 'No existe', traceId: 'abc' })).toEqual({
      code: 'not_found',
      message: 'No existe',
      details: undefined,
      traceId: 'abc',
    });
  });

  it('rechaza formas ajenas sin asumir', () => {
    expect(parseErrorBody(null)).toBeNull();
    expect(parseErrorBody({ code: 1, message: 'x' })).toBeNull();
    expect(parseErrorBody({})).toBeNull();
  });
});

describe('requestJson', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('lanza ApiError con code y traceId del contrato', async () => {
    const fake = vi.mocked(fetch);
    fake.mockResolvedValueOnce(
      new Response(JSON.stringify({ code: 'invalid_request', message: 'Mal', traceId: 't-1' }), {
        status: 422,
        headers: { 'X-Trace-Id': 't-1' },
      }),
    );
    await expect(requestJson('/api/x', { timeoutMs: 1000 })).rejects.toMatchObject({
      code: 'invalid_request',
      status: 422,
      traceId: 't-1',
    });
  });

  it('conserva Retry-After en 429', async () => {
    const fake = vi.mocked(fetch);
    fake.mockResolvedValueOnce(
      new Response(JSON.stringify({ code: 'rate_limited', message: 'Lento' }), {
        status: 429,
        headers: { 'Retry-After': '20', 'X-Trace-Id': 't-9' },
      }),
    );
    try {
      await requestJson('/api/x', { timeoutMs: 1000 });
      throw new Error('debió lanzar rate_limited');
    } catch (e) {
      const err = e as ApiError;
      expect(err.code).toBe('rate_limited');
      expect(err.retryAfter).toBe('20');
    }
  });

  it('mapea la caída de red a code network', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new TypeError('down'));
    await expect(requestJson('/api/x', { timeoutMs: 1000 })).rejects.toMatchObject({ code: 'network' });
  });
});
