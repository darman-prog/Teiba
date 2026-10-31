import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SensorStrip } from './SensorStrip';
import { FIXTURE_SENSORS } from '../../test/fixtures';

// El transecto se lee como riel de estación: readout y nodos numerados.
describe('SensorStrip', () => {
  const noop = () => {};

  it('muestra el readout de nodos y revisión', () => {
    render(<SensorStrip items={FIXTURE_SENSORS.items} loading={false} onAsk={noop} onRefresh={noop} />);
    expect(screen.getByText(/05 nodos/i)).toBeInTheDocument();
    expect(screen.getByText(/en revisión/i)).toBeInTheDocument();
  });

  it('numera cada ficha en base 01', () => {
    render(<SensorStrip items={FIXTURE_SENSORS.items.slice(0, 2)} loading={false} onAsk={noop} onRefresh={noop} />);
    expect(screen.getByText('01')).toBeInTheDocument();
    expect(screen.getByText('02')).toBeInTheDocument();
  });

  it('el botón Actualizar conserva su texto visible', () => {
    const onRefresh = vi.fn();
    render(<SensorStrip items={[]} loading={false} onAsk={noop} onRefresh={onRefresh} />);
    expect(screen.getByRole('button', { name: /actualizar/i })).toBeInTheDocument();
  });
});
