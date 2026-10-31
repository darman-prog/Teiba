import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { axe } from 'vitest-axe';
import App from '../app/App';

// Axe sobre la app con fixtures: sin violaciones críticas.
describe('axe App', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_USE_MOCKS', 'true');
    sessionStorage.setItem('teiba-role', 'admin');
  });

  it('estación sin violaciones', async () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/sage']}>
        <App />
      </MemoryRouter>,
    );
    // Espera a que el transecto mock cargue antes del análisis.
    await new Promise((r) => setTimeout(r, 400));
    const results = await axe(container);
    expect(results.violations).toEqual([]);
  }, 15000);

  it('libro sin violaciones', async () => {
    sessionStorage.setItem('teiba-role', 'user');
    const { container } = render(
      <MemoryRouter initialEntries={['/parques']}>
        <App />
      </MemoryRouter>,
    );
    await new Promise((r) => setTimeout(r, 400));
    const results = await axe(container);
    expect(results.violations).toEqual([]);
  }, 15000);
});
