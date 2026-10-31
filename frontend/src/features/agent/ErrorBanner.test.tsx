import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBanner } from './ErrorBanner';
import { ApiError } from '../../api/errors';

describe('ErrorBanner', () => {
  const err = new ApiError({ code: 'db_unavailable', message: 'Caída', status: 503, traceId: 't-abc' });

  it('anuncia con role=alert, muestra traceId y reintenta', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    const onDismiss = vi.fn();
    render(<ErrorBanner error={err} pregunta="¿Cómo está SS-01?" onRetry={onRetry} onDismiss={onDismiss} />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByTestId('trace-id')).toHaveTextContent('t-abc');
    expect(screen.getByText(/pregunta conservada/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /reintentar/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
    await user.click(screen.getByRole('button', { name: /descartar/i }));
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});
