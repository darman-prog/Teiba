import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SensorCard } from './SensorCard';
import { FIXTURE_SENSORS } from '../../test/fixtures';

// Los cuatro estados usan icono + texto, nunca solo color.
describe('SensorCard', () => {
  const base = FIXTURE_SENSORS.items[0]!;
  const cases = [
    { estado: 'ok', label: 'En rango' },
    { estado: 'warning', label: 'Revisar' },
    { estado: 'danger', label: 'Fuera de rango' },
    { estado: 'sin_datos', label: 'Sin datos' },
  ] as const;

    for (const { estado, label } of cases) {
    it(`muestra ${estado} con texto "${label}"`, () => {
      const sensor = estado === 'sin_datos'
        ? { ...base, id: 'MET-01', estado, ultima_lectura: null as never }
        : { ...base, estado };
      render(<SensorCard sensor={sensor} index={0} />);
      expect(screen.getByText(label)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: new RegExp(sensor.id) })).toBeInTheDocument();
    });
  }

  it('numera el nodo en base 01 como riel de estación', () => {
    render(<SensorCard sensor={base} index={2} />);
    expect(screen.getByText('03')).toBeInTheDocument();
  });

  it('no enmascara sector ni lectura para lector de pantalla', () => {
    render(<SensorCard sensor={base} index={0} />);
    const btn = screen.getByRole('button', { name: new RegExp(base.id) });
    expect(btn.textContent).toMatch(/Sector Norte/);
  });
});
