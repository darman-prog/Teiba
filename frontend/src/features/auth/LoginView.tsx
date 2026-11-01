import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ApiError } from '../../api/errors';
import { useAuth } from '../../app/AuthProvider';
import { destinoSeguro, homeForPerfil } from '../../lib/navigation';
import { Button } from '../../shared/ui/Button';

function mensajeError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.code === 'invalid_credentials') return 'Correo o contraseña incorrectos.';
    if (err.code === 'rate_limited') return 'Demasiados intentos. Espera unos segundos.';
    if (err.code === 'network') return 'Sin conexión con la API. Verifica el backend.';
    if (err.code === 'timeout') return 'El servidor tardó demasiado. Intenta de nuevo.';
    if (err.status === 503) return 'El servicio de acceso no está disponible.';
    return err.message;
  }
  return 'No se pudo iniciar sesión. Intenta de nuevo.';
}

export function LoginView() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (enviando) return;
    setError(null);
    setEnviando(true);
    try {
      const data = await login(correo, contrasena);
      const from = destinoSeguro(location.state);
      navigate(from ?? homeForPerfil(data.usuario, data.perfil), { replace: true });
    } catch (err) {
      setError(mensajeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section aria-labelledby="login-title" className="mx-auto mt-6 max-w-md">
      <div className="rounded-[8px] border border-border bg-surface p-5">
        <p className="field-label">Acceso local</p>
        <h1 id="login-title" className="mt-1 font-display text-[20px] font-semibold text-ink">
          Entrar a Teiba
        </h1>
        <p className="mt-1 text-[13px] text-ink-2">
          Usa tu cuenta de demostración. La sesión queda en una cookie httpOnly.
        </p>

        <form className="mt-4 flex flex-col gap-3" onSubmit={onSubmit}>
          <div className="flex flex-col gap-1">
            <label htmlFor="login-correo" className="field-label">
              Correo
            </label>
            <input
              id="login-correo"
              type="email"
              autoComplete="username"
              required
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              disabled={enviando}
              className="rounded-[6px] border border-border bg-surface px-3 py-2 text-[14px] text-ink"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="login-contrasena" className="field-label">
              Contraseña
            </label>
            <input
              id="login-contrasena"
              type="password"
              autoComplete="current-password"
              required
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              disabled={enviando}
              className="rounded-[6px] border border-border bg-surface px-3 py-2 text-[14px] text-ink"
            />
          </div>

          {error && (
            <p role="alert" className="rounded-[6px] border border-danger/40 bg-danger-soft px-3 py-2 text-[13px] text-danger">
              {error}
            </p>
          )}

          <Button type="submit" disabled={enviando}>
            {enviando ? 'Entrando…' : 'Entrar'}
          </Button>
        </form>
      </div>
    </section>
  );
}
