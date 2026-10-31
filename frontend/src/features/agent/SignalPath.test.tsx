import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { SignalPath } from './SignalPath';
import { FIXTURE_CONSULTA } from '../../test/fixtures';
import type { ChatMessage } from '../../hooks/useAgent';

const MSG: ChatMessage = {
  id: 'a-1',
  role: 'assistant',
  texto: 'Respuesta demo',
  trazas: FIXTURE_CONSULTA.trazas,
  meta: FIXTURE_CONSULTA.meta,
  traceId: 'demo-trace-001',
};

describe('SignalPath', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('muestra ayuda cuando no hay mensaje seleccionado', () => {
    render(<SignalPath message={null} />);
    expect(screen.getByText(/selecciona.*ver n trazas/i)).toBeInTheDocument();
  });

  it('lista las 3 trazas sin mezclar turnos y expande el crudo', async () => {
    const user = (await import('@testing-library/user-event')).default.setup();
    render(<SignalPath message={MSG} />);
    expect(screen.getByText(/3 herramientas/i)).toBeInTheDocument();
    expect(screen.getByText('list_sensors')).toBeInTheDocument();
    expect(screen.getByText('get_sensor_history')).toBeInTheDocument();
    expect(screen.getByText('get_device_context')).toBeInTheDocument();
    // El resultado crudo es string con scroll, no objeto.
    expect(screen.getByText(/"estado": "ok"/)).toBeInTheDocument();
    // El detalle expandido permite copiar args + resultado.
    expect(screen.getByRole('button', { name: /copiar/i })).toBeInTheDocument();
    // Colapsar y expandir con aria-expanded.
    const btn = screen.getByRole('button', { name: /list_sensors/i });
    expect(btn).toHaveAttribute('aria-expanded', 'true');
    await user.click(btn);
    expect(btn).toHaveAttribute('aria-expanded', 'false');
    await waitFor(() => expect(screen.queryByText(/"estado": "ok"/)).not.toBeInTheDocument());
  });
});
