import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../app/App';

// La app corre en modo demo para no tocar la red en pruebas.
describe('roles y guard', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_USE_MOCKS', 'true');
    sessionStorage.clear();
  });

  it('admin abre la estación en /sage', async () => {
    sessionStorage.setItem('teiba-role', 'admin');
    render(
      <MemoryRouter initialEntries={['/sage']}>
        <App />
      </MemoryRouter>,
    );
    expect(await screen.findByRole('heading', { name: /bitácora de campo/i })).toBeInTheDocument();
  });

  it('usuario en /sage redirige al libro', async () => {
    sessionStorage.setItem('teiba-role', 'user');
    render(
      <MemoryRouter initialEntries={['/sage']}>
        <App />
      </MemoryRouter>,
    );
    expect(await screen.findByRole('heading', { name: /libro de parques/i })).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('heading', { name: /bitácora de campo/i })).not.toBeInTheDocument());
  });

  it('raíz redirige según rol', async () => {
    sessionStorage.setItem('teiba-role', 'user');
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );
    expect(await screen.findByRole('heading', { name: /libro de parques/i })).toBeInTheDocument();
  });
});
