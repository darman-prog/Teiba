import { useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ApiError } from '../../api/errors';
import { useAuth } from '../../app/AuthProvider';
import { destinoSeguro, homeForPerfil } from '../../lib/navigation';
import { Button } from '../../shared/ui/Button';
import { AuthField } from './AuthField';
import { AuthLayout } from './AuthLayout';

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
    <AuthLayout
      kicker="Acceso local"
      title="Entrar a Teiba"
      intro="Usa tu cuenta de demostración. La sesión queda en una cookie HttpOnly y el rol se decide en el servidor."
      footer={
        <p>
          ¿Aún no tienes cuenta?{' '}
          <Link
            to="/registro"
            className="font-semibold text-moss underline decoration-copper decoration-2 underline-offset-4 hover:text-moss-deep"
          >
            Crear cuenta de ciudadano
          </Link>
        </p>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={onSubmit} aria-busy={enviando}>
        <AuthField
          id="login-correo"
          label="Correo"
          type="email"
          autoComplete="username"
          required
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          disabled={enviando}
          placeholder="nombre@teiba.local"
        />

        <AuthField
          id="login-contrasena"
          label="Contraseña"
          type="password"
          autoComplete="current-password"
          required
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
          disabled={enviando}
        />

        {error && (
          <p
            role="alert"
            className="rounded-[6px] border border-danger/40 bg-danger-soft px-3 py-2 text-[13px] font-semibold text-danger"
          >
            {error}
          </p>
        )}

        <Button type="submit" disabled={enviando} className="w-full">
          {enviando ? 'Entrando…' : 'Entrar'}
        </Button>
      </form>
    </AuthLayout>
  );
}
