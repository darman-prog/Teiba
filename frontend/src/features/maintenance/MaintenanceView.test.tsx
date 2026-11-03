import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '../../app/AuthProvider';
import type { MaintenanceItem, SessionResponse } from '../../types/api';
import { MaintenanceView } from './MaintenanceView';

const api = vi.hoisted(() => ({
  fetchMe: vi.fn(),
  postLogin: vi.fn(),
  postLogout: vi.fn(),
  fetchMantenimientos: vi.fn(),
  fetchOperadores: vi.fn(),
  changeMantenimientoEstado: vi.fn(),
  reassignMantenimiento: vi.fn(),
  changeIncidenteEstado: vi.fn(),
}));

vi.mock('../../api/auth', () => ({
  fetchMe: api.fetchMe,
  postLogin: api.postLogin,
  postLogout: api.postLogout,
}));

vi.mock('../../api/maintenance', () => ({
  fetchMantenimientos: api.fetchMantenimientos,
  fetchOperadores: api.fetchOperadores,
  fetchIncidentes: vi.fn(async () => ({ items: [], total: 0 })),
  fetchElementos: vi.fn(async () => ({ items: [], total: 0 })),
  createMantenimiento: vi.fn(),
  changeMantenimientoEstado: api.changeMantenimientoEstado,
  reassignMantenimiento: api.reassignMantenimiento,
  changeIncidenteEstado: api.changeIncidenteEstado,
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

const TAREA: MaintenanceItem = {
  id: '671153000000000000000001',
  tipo: 'correctivo',
  descripcion: 'Ajustar tornillo',
  prioridad: 'alta',
  estado: 'pendiente',
  fecha_programada: '2026-10-30T08:00:00Z',
  fecha_ejecucion: null,
  fecha_reapertura: null,
  nota_cierre: null,
  nota_reapertura: null,
  costo_estimado: 120000,
  vencida: true,
  parque: { id: 'p1', codigo: 'PRQ-001', nombre: 'Parque San Pío' },
  responsable: { id: 'operador-mongo', nombre: 'Óscar Operador', rol: 'operador_mantenimiento' },
  incidente: null,
  elemento: null,
};

function renderView(session: SessionResponse) {
  api.fetchMe.mockResolvedValue({ data: session, traceId: null });
  api.fetchMantenimientos.mockResolvedValue({ items: [TAREA], total: 1 });
  api.fetchOperadores.mockResolvedValue({
    items: [{ id: 'operador-mongo', nombre: 'Óscar Operador' }],
    total: 1,
  });
  return render(
    <AuthProvider>
      <MaintenanceView />
    </AuthProvider>,
  );
}

describe('MaintenanceView', () => {
  beforeEach(() => {
    api.fetchMe.mockReset();
    api.fetchMantenimientos.mockReset();
    api.fetchOperadores.mockReset();
    api.changeMantenimientoEstado.mockReset();
    api.reassignMantenimiento.mockReset();
    api.changeIncidenteEstado.mockReset();
  });

  it('admin finaliza con nota', async () => {
    const user = userEvent.setup();
    api.changeMantenimientoEstado.mockResolvedValue({ ...TAREA, estado: 'finalizado' });
    renderView(ADMIN);
    await screen.findByRole('heading', { name: /^mantenimientos$/i });
    await user.click(screen.getByRole('button', { name: /ajustar tornillo/i }));
    const nota = await screen.findByLabelText(/nota de cierre/i);
    await user.type(nota, 'Tornillo ajustado.');
    await user.click(screen.getByRole('button', { name: /finalizar tarea/i }));
    expect(api.changeMantenimientoEstado).toHaveBeenCalledWith(TAREA.id, {
      estado: 'finalizado',
      nota: 'Tornillo ajustado.',
    });
  });

  it('operator inicia su tarea', async () => {
    const user = userEvent.setup();
    api.changeMantenimientoEstado.mockResolvedValue({ ...TAREA, estado: 'en_proceso' });
    renderView(OPERATOR);
    await screen.findByRole('heading', { name: /mis tareas/i });
    await user.click(screen.getByRole('button', { name: /ajustar tornillo/i }));
    await user.click(await screen.findByRole('button', { name: /iniciar tarea/i }));
    expect(api.changeMantenimientoEstado).toHaveBeenCalledWith(TAREA.id, {
      estado: 'en_proceso',
      nota: null,
    });
  });
});
