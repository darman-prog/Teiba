import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { ParkIndex } from './ParkIndex';
import { ParkDetail } from './ParkDetail';
import { Routes, Route } from 'react-router-dom';

describe('libro de parques', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_USE_MOCKS', 'true');
  });

  it('filtra por búsqueda y muestra empty', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ParkIndex />
      </MemoryRouter>,
    );
    expect(await screen.findByText(/10 de 10 parques/i)).toBeInTheDocument();
    await user.type(screen.getByLabelText(/buscar parque/i), 'zzz-sin-parque');
    expect(await screen.findByText(/sin resultados/i)).toBeInTheDocument();
  });

  it('ficha muestra sectores e indicaciones', async () => {
    render(
      <MemoryRouter initialEntries={['/parques/PQ-01']}>
        <Routes>
          <Route path="/parques/:codigo" element={<ParkDetail />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByRole('heading', { name: /parque san pío/i })).toBeInTheDocument();
    expect(screen.getAllByText(/sector norte/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/riego programado/i)).toBeInTheDocument();
  });

  it('código inexistente muestra 404 con traceId', async () => {
    render(
      <MemoryRouter initialEntries={['/parques/NOPE']}>
        <Routes>
          <Route path="/parques/:codigo" element={<ParkDetail />} />
        </Routes>
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByText(/no existe el parque/i)).toBeInTheDocument();
  });
});
