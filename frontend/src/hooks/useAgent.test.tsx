import { describe, expect, it, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAgent } from './useAgent';
import { ApiError } from '../api/errors';

vi.mock('../api/agent', () => ({
  postConsulta: vi.fn(),
}));

import { postConsulta } from '../api/agent';
import { FIXTURE_CONSULTA } from '../test/fixtures';

describe('useAgent', () => {
  beforeEach(() => {
    vi.mocked(postConsulta).mockReset();
  });

  it('guarda cada respuesta con sus trazas y selecciona el turno', async () => {
    vi.mocked(postConsulta).mockResolvedValueOnce({ data: FIXTURE_CONSULTA, traceId: 't-1' });
    const { result } = renderHook(() => useAgent());
    await act(async () => {
      await result.current.send('¿Cómo está SS-01?');
    });
    await waitFor(() => expect(result.current.messages.length).toBe(2));
    const [q, a] = result.current.messages;
    expect(q!.role).toBe('user');
    expect(a!.trazas.length).toBe(3);
    expect(result.current.selectedId).toBe(a!.id);
  });

  it('conserva la pregunta fallida para reintento', async () => {
    vi.mocked(postConsulta)
      .mockRejectedValueOnce(new ApiError({ code: 'timeout', message: 'Lento', status: 504 }))
      .mockResolvedValueOnce({ data: FIXTURE_CONSULTA, traceId: 't-2' });
    const { result } = renderHook(() => useAgent());
    await act(async () => {
      await result.current.send('¿Qué sensores dependen de ANT-01?');
    });
    await waitFor(() => expect(result.current.error?.code).toBe('timeout'));
    expect(result.current.lastFailed).toContain('ANT-01');
    await act(async () => {
      await result.current.retry();
    });
    await waitFor(() => expect(result.current.error).toBeNull());
  });
});
