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
  postRegister: vi.fn(),
}));

vi.mock('../../api/auth', () => auth);

const CIUDADANO: SessionResponse = {
  usuario: { correo: 'nueva@teiba.local', rol: 'user' },
  perfil: {
    id: 'nueva-mongo',
    nombre: 'Nueva Ciudadana',
    correo: 'nueva@teiba.local',
    rol: 'ciudadano',
  },
  expira_en: '2026-11-09T20:00:00Z',
};

function renderRegistro() {
  return render(
    <MemoryRouter initialEntries={['/registro']}>
      <App />
    </MemoryRouter>,
  );
}

async function llenar(correo: string, contrasena: string, confirmacion = contrasena) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/^correo$/i), correo);
  await user.type(screen.getByLabelText(/^contraseña$/i), contrasena);
  await user.type(screen.getByLabelText(/repetir contraseña/i), confirmacion);
  return user;
}

describe('RegisterView', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_USE_MOCKS', 'true');
    auth.fetchMe.mockReset();
    auth.postLogin.mockReset();
    auth.postLogout.mockReset();
    auth.postRegister.mockReset();
    auth.fetchMe.mockRejectedValue(
      new ApiError({ code: 'not_authenticated', message: 'Sin sesión', status: 401 }),
    );
    auth.postLogout.mockResolvedValue({ data: null, traceId: null });
  });

  it('valida la longitud mínima antes de llamar a la API', async () => {
    renderRegistro();
    await screen.findByRole('heading', { name: /crear cuenta de ciudadano/i });
    const user = await llenar('nueva@teiba.local', 'corta');
    await user.click(screen.getByRole('button', { name: /^crear cuenta$/i }));

    expect(screen.getByText(/al menos 12 caracteres/i)).toBeInTheDocument();
    expect(auth.postRegister).not.toHaveBeenCalled();
  });

  it('exige que las contraseñas coincidan', async () => {
    renderRegistro();
    await screen.findByRole('heading', { name: /crear cuenta de ciudadano/i });
    const user = await llenar('nueva@teiba.local', 'clave-segura-123', 'otra-clave-123');
    await user.click(screen.getByRole('button', { name: /^crear cuenta$/i }));

    expect(screen.getByText(/no coinciden/i)).toBeInTheDocument();
    expect(auth.postRegister).not.toHaveBeenCalled();
  });

  it('crea la cuenta y entra al libro de parques', async () => {
    auth.postRegister.mockResolvedValueOnce({ data: CIUDADANO, traceId: null });
    renderRegistro();
    await screen.findByRole('heading', { name: /crear cuenta de ciudadano/i });
    const user = await llenar('nueva@teiba.local', 'clave-segura-123');
    await user.click(screen.getByRole('button', { name: /^crear cuenta$/i }));

    expect(await screen.findByRole('heading', { name: /libro de parques/i })).toBeInTheDocument();
    expect(auth.postRegister).toHaveBeenCalledWith('nueva@teiba.local', 'clave-segura-123', undefined);
  });

  it('muestra el correo duplicado sin filtrar datos internos', async () => {
    auth.postRegister.mockRejectedValueOnce(
      new ApiError({ code: 'email_taken', message: 'Ya existe', status: 409 }),
    );
    renderRegistro();
    await screen.findByRole('heading', { name: /crear cuenta de ciudadano/i });
    const user = await llenar('nueva@teiba.local', 'clave-segura-123');
    await user.click(screen.getByRole('button', { name: /^crear cuenta$/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/ya tiene una cuenta/i);
  });

  it('enviando deshabilita el botón', async () => {
    auth.postRegister.mockImplementation(() => new Promise(() => {}));
    renderRegistro();
    await screen.findByRole('heading', { name: /crear cuenta de ciudadano/i });
    const user = await llenar('nueva@teiba.local', 'clave-segura-123');
    await user.click(screen.getByRole('button', { name: /^crear cuenta$/i }));

    expect(screen.getByRole('button', { name: /creando cuenta/i })).toBeDisabled();
  });
});
