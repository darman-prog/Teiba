import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ApiError } from '../../api/errors';
import { useAuth } from '../../app/AuthProvider';
import { homeForPerfil } from '../../lib/navigation';
import { Button } from '../../shared/ui/Button';
import { AuthField } from './AuthField';
import { AuthLayout } from './AuthLayout';

const MIN_PASSWORD = 12;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

interface Errores {
  correo?: string;
  contrasena?: string;
  confirmacion?: string;
}

function validar(correo: string, contrasena: string, confirmacion: string): Errores {
  const errores: Errores = {};
  if (!EMAIL_RE.test(correo.trim())) errores.correo = 'Escribe un correo válido.';
  if (contrasena.length < MIN_PASSWORD) {
    errores.contrasena = `Usa al menos ${MIN_PASSWORD} caracteres.`;
  } else if (new TextEncoder().encode(contrasena).length > 72) {
    errores.contrasena = 'La contraseña no puede superar 72 bytes.';
  }
  if (confirmacion !== contrasena) errores.confirmacion = 'Las contraseñas no coinciden.';
  return errores;
}

function mensajeError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.code === 'email_taken') return 'Ese correo ya tiene una cuenta. Inicia sesión.';
    if (err.code === 'rate_limited') return 'Demasiados registros. Espera unos segundos.';
    if (err.code === 'network') return 'Sin conexión con la API. Verifica el backend.';
    if (err.code === 'timeout') return 'El servidor tardó demasiado. Intenta de nuevo.';
    if (err.status === 503) return 'La base de datos no está disponible. Intenta más tarde.';
    return err.message;
  }
  return 'No se pudo crear la cuenta. Intenta de nuevo.';
}

export function RegisterView() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const formRef = useRef<HTMLFormElement>(null);
  const [nombre, setNombre] = useState('');
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [confirmacion, setConfirmacion] = useState('');
  const [errores, setErrores] = useState<Errores>({});
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    // Se enfoca después del render para que el error ya esté asociado al campo.
    const primero = (['correo', 'contrasena', 'confirmacion'] as const).find(
      (campo) => errores[campo],
    );
    if (primero) document.getElementById(`registro-${primero}`)?.focus();
  }, [errores]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (enviando) return;
    setError(null);

    const encontrados = validar(correo, contrasena, confirmacion);
    setErrores(encontrados);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    try {
      const data = await register(correo, contrasena, nombre);
      navigate(homeForPerfil(data.usuario, data.perfil), { replace: true });
    } catch (err) {
      setError(mensajeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <AuthLayout
      kicker="Registro público"
      title="Crear cuenta de ciudadano"
      intro="Con tu cuenta puedes consultar el libro de parques y seguir el estado de los sensores. El rol lo asigna el servidor."
      footer={
        <p>
          ¿Ya tienes cuenta?{' '}
          <Link
            to="/login"
            className="font-semibold text-moss underline decoration-copper decoration-2 underline-offset-4 hover:text-moss-deep"
          >
            Entrar a Teiba
          </Link>
        </p>
      }
    >
      <form ref={formRef} className="flex flex-col gap-4" onSubmit={onSubmit} aria-busy={enviando}>
        <AuthField
          id="registro-nombre"
          label="Nombre (opcional)"
          type="text"
          autoComplete="name"
          maxLength={80}
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          disabled={enviando}
          placeholder="Cómo quieres aparecer"
        />

        <AuthField
          id="registro-correo"
          label="Correo"
          type="email"
          autoComplete="username"
          required
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          disabled={enviando}
          placeholder="nombre@teiba.local"
          error={errores.correo}
        />

        <AuthField
          id="registro-contrasena"
          label="Contraseña"
          type="password"
          autoComplete="new-password"
          required
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
          disabled={enviando}
          hint={`Mínimo ${MIN_PASSWORD} caracteres.`}
          error={errores.contrasena}
        />

        <AuthField
          id="registro-confirmacion"
          label="Repetir contraseña"
          type="password"
          autoComplete="new-password"
          required
          value={confirmacion}
          onChange={(e) => setConfirmacion(e.target.value)}
          disabled={enviando}
          error={errores.confirmacion}
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
          {enviando ? 'Creando cuenta…' : 'Crear cuenta'}
        </Button>
      </form>
    </AuthLayout>
  );
}
