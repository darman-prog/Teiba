import { describe, expect, it, vi } from 'vitest';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { axe } from 'vitest-axe';
import App from './App';
import { ApiError } from '../api/errors';
import type { SessionResponse } from '../types/api';

const state = vi.hoisted(() => ({ session: null as unknown, fail: null as unknown }));

vi.mock('../api/auth', () => ({
  fetchMe: vi.fn(async () => {
    if (state.fail) throw state.fail;
    return { data: state.session, traceId: null };
  }),
  postLogin: vi.fn(),
  postLogout: vi.fn(async () => ({ data: null, traceId: null })),
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

const SIN_PERFIL: SessionResponse = {
  usuario: { correo: 'operador@teiba.local', rol: 'operator' },
  perfil: null,
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

async function renderizar(path: string, session: SessionResponse | null, fail?: unknown) {
  state.session = session;
  state.fail = fail ?? null;
  const { container } = render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
  await new Promise((resolve) => setTimeout(resolve, 400));
  return container;
}

describe('axe auth', () => {
  it('login sin violaciones', async () => {
    const container = await renderizar(
      '/login',
      null,
      new ApiError({ code: 'not_authenticated', message: 'Sin sesión', status: 401 }),
    );
    expect((await axe(container)).violations).toEqual([]);
  }, 15000);

  it('estación admin sin violaciones', async () => {
    const container = await renderizar('/sage', ADMIN);
    expect((await axe(container)).violations).toEqual([]);
  }, 15000);

  it('perfil no configurado sin violaciones', async () => {
    const container = await renderizar('/perfil-no-configurado', SIN_PERFIL);
    expect((await axe(container)).violations).toEqual([]);
  }, 15000);

  it('libro sin violaciones', async () => {
    const container = await renderizar('/parques', USER);
    expect((await axe(container)).violations).toEqual([]);
  }, 15000);

  it('mantenimientos admin sin violaciones', async () => {
    const container = await renderizar('/mantenimientos', ADMIN);
    expect((await axe(container)).violations).toEqual([]);
  }, 15000);

  it('mis tareas del operador sin violaciones', async () => {
    const container = await renderizar('/mantenimientos', OPERATOR);
    expect((await axe(container)).violations).toEqual([]);
  }, 15000);
});
