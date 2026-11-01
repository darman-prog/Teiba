import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '../../app/App';
import { ApiError } from '../../api/errors';
import type { SessionResponse } from '../../types/api';

const auth = vi.hoisted(() => ({
  fetchMe: vi.fn(),
  postLogin: vi.fn(),
  postLogout: vi.fn(),
}));

vi.mock('../../api/auth', () => auth);

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

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <App />
    </MemoryRouter>,
  );
}

async function completarFormulario() {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/correo/i), 'admin@teiba.local');
  await user.type(screen.getByLabelText(/contraseña/i), 'admin12345678');
  return user;
}

describe('LoginView', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_USE_MOCKS', 'true');
    auth.fetchMe.mockReset();
    auth.postLogin.mockReset();
    auth.postLogout.mockReset();
    auth.fetchMe.mockRejectedValue(
      new ApiError({ code: 'not_authenticated', message: 'Sin sesión', status: 401 }),
    );
    auth.postLogout.mockResolvedValue({ data: null, traceId: null });
  });

  it('muestra error de credenciales y conserva el formulario', async () => {
    auth.postLogin.mockRejectedValueOnce(
      new ApiError({ code: 'invalid_credentials', message: 'Mal', status: 401 }),
    );
    renderLogin();
    await screen.findByRole('heading', { name: /entrar a teiba/i });
    const user = await completarFormulario();
    await user.click(screen.getByRole('button', { name: /^entrar$/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/correo o contraseña/i);
    expect(screen.getByLabelText(/correo/i)).toHaveValue('admin@teiba.local');
  });

  it('muestra rate limit con su mensaje', async () => {
    auth.postLogin.mockRejectedValueOnce(
      new ApiError({ code: 'rate_limited', message: 'Lento', status: 429 }),
    );
    renderLogin();
    await screen.findByRole('heading', { name: /entrar a teiba/i });
    const user = await completarFormulario();
    await user.click(screen.getByRole('button', { name: /^entrar$/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/demasiados intentos/i);
  });

  it('enviando deshabilita el botón', async () => {
    auth.postLogin.mockImplementation(() => new Promise(() => {}));
    renderLogin();
    await screen.findByRole('heading', { name: /entrar a teiba/i });
    const user = await completarFormulario();
    await user.click(screen.getByRole('button', { name: /^entrar$/i }));
    expect(screen.getByRole('button', { name: /entrando/i })).toBeDisabled();
  });

  it('login admin navega a la estación', async () => {
    auth.postLogin.mockResolvedValueOnce({ data: ADMIN, traceId: null });
    renderLogin();
    await screen.findByRole('heading', { name: /entrar a teiba/i });
    const user = await completarFormulario();
    await user.click(screen.getByRole('button', { name: /^entrar$/i }));
    expect(await screen.findByRole('heading', { name: /bitácora de campo/i })).toBeInTheDocument();
  });
});
