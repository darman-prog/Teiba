import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import { ApiError } from '../api/errors';
import type { SessionResponse } from '../types/api';

const state = vi.hoisted(() => ({
  session: null as unknown,
  fail: null as unknown,
}));

vi.mock('../api/auth', () => ({
  fetchMe: vi.fn(async () => {
    if (state.fail) throw state.fail;
    return { data: state.session, traceId: null };
  }),
  postLogin: vi.fn(),
  postLogout: vi.fn(async () => ({ data: null, traceId: null })),
  postRegister: vi.fn(),
}));

vi.mock('../api/maintenance', () => ({
  fetchMantenimientos: vi.fn(async () => ({ items: [], total: 0 })),
  fetchOperadores: vi.fn(async () => ({ items: [], total: 0 })),
  fetchIncidentes: vi.fn(async () => ({ items: [], total: 0 })),
  fetchElementos: vi.fn(async () => ({ items: [], total: 0 })),
  createMantenimiento: vi.fn(),
  changeMantenimientoEstado: vi.fn(),
  reassignMantenimiento: vi.fn(),
  changeIncidenteEstado: vi.fn(),
}));

const ADMIN: SessionResponse = {
  usuario: { correo: 'admin@teiba.local', rol: 'admin' },
  perfil: {
    id: 'admin-mongo',
    nombre: 'Ana Administradora',
    correo: 'admin@teiba.local',
    rol: 'administrador',
  },
  expira_en: '2026-10-31T20:00:00Z',
};

const OPERATOR: SessionResponse = {
  usuario: { correo: 'operador@teiba.local', rol: 'operator' },
  perfil: {
    id: 'operador-mongo',
    nombre: 'Óscar Operador',
    correo: 'operador@teiba.local',
    rol: 'operador_mantenimiento',
  },
  expira_en: '2026-10-31T20:00:00Z',
};

const USER: SessionResponse = {
  usuario: { correo: 'user@teiba.local', rol: 'user' },
  perfil: {
    id: 'user-mongo',
    nombre: 'Carla Ciudadana',
    correo: 'user@teiba.local',
    rol: 'ciudadano',
  },
  expira_en: '2026-10-31T20:00:00Z',
};

const NO_PROFILE: SessionResponse = {
  usuario: { correo: 'operador@teiba.local', rol: 'operator' },
  perfil: null,
  expira_en: '2026-10-31T20:00:00Z',
};

function renderAt(path: string, session: SessionResponse | null, fail?: unknown) {
  state.session = session;
  state.fail = fail ?? null;
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

const ANONIMO = new ApiError({ code: 'not_authenticated', message: 'Sin sesión', status: 401 });

describe('auth y guards', () => {
  beforeEach(() => {
    state.session = null;
    state.fail = null;
    vi.stubEnv('VITE_USE_MOCKS', 'true');
  });

  it('anónimo en /sage va a login', async () => {
    renderAt('/sage', null, ANONIMO);
    expect(await screen.findByRole('heading', { name: /entrar a teiba/i })).toBeInTheDocument();
  });

  it('anónimo en /registro ve el alta de ciudadano', async () => {
    renderAt('/registro', null, ANONIMO);
    expect(
      await screen.findByRole('heading', { name: /crear cuenta de ciudadano/i }),
    ).toBeInTheDocument();
  });

  it('autenticado en /registro va a su home', async () => {
    renderAt('/registro', OPERATOR);
    expect(await screen.findByRole('heading', { name: /mis tareas/i })).toBeInTheDocument();
  });

  it('admin abre la estación', async () => {
    renderAt('/sage', ADMIN);
    expect(await screen.findByRole('heading', { name: /bitácora de campo/i })).toBeInTheDocument();
  });

  it('admin con perfil administrador puede ver mantenimientos', async () => {
    renderAt('/mantenimientos', ADMIN);
    expect(await screen.findByRole('heading', { name: /^mantenimientos$/i })).toBeInTheDocument();
  });

  it('operator con perfil operador puede ver mantenimientos', async () => {
    renderAt('/mantenimientos', OPERATOR);
    expect(await screen.findByRole('heading', { name: /mis tareas/i })).toBeInTheDocument();
  });

  it('operator sin perfil no entra a mantenimientos', async () => {
    renderAt('/mantenimientos', NO_PROFILE);
    expect(await screen.findByRole('heading', { name: /perfil no configurado/i })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /en construcción/i })).not.toBeInTheDocument();
  });

  it('user en /sage va al libro', async () => {
    renderAt('/sage', USER);
    expect(await screen.findByRole('heading', { name: /libro de parques/i })).toBeInTheDocument();
  });

  it('user con perfil elevado no abre mantenimientos', async () => {
    renderAt('/mantenimientos', {
      ...USER,
      perfil: { ...USER.perfil!, rol: 'operador_mantenimiento' },
    });
    expect(await screen.findByRole('heading', { name: /perfil no configurado/i })).toBeInTheDocument();
  });

  it('logout limpia la sesión y vuelve a login', async () => {
    const user = userEvent.setup();
    renderAt('/sage', ADMIN);
    await screen.findByRole('heading', { name: /bitácora de campo/i });
    await user.click(screen.getByText('Ana Administradora'));
    await user.click(screen.getByRole('button', { name: /cerrar sesión/i }));
    expect(await screen.findByRole('heading', { name: /entrar a teiba/i })).toBeInTheDocument();
  });
});
