import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { fetchMe, postLogin, postLogout } from '../api/auth';
import { ApiError } from '../api/errors';
import type { AuthUser, PerfilUsuario, SessionResponse } from '../types/api';

type Status = 'loading' | 'anonymous' | 'authenticated' | 'error';

interface AuthContextValue {
  status: Status;
  usuario: AuthUser | null;
  perfil: PerfilUsuario | null;
  error: string | null;
  login: (correo: string, contrasena: string) => Promise<SessionResponse>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const Ctx = createContext<AuthContextValue | null>(null);

// Sesión de la SPA: cookie httpOnly, sin token en JS ni localStorage.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>('loading');
  const [usuario, setUsuario] = useState<AuthUser | null>(null);
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [error, setError] = useState<string | null>(null);

  const clear = useCallback(() => {
    setUsuario(null);
    setPerfil(null);
    setStatus('anonymous');
    setError(null);
  }, []);

  const refresh = useCallback(async () => {
    setStatus('loading');
    setError(null);
    try {
      const { data } = await fetchMe();
      setUsuario(data.usuario);
      setPerfil(data.perfil);
      setStatus('authenticated');
    } catch (err) {
      // Un 401 es ausencia de sesión, no un error de la pantalla.
      if (err instanceof ApiError && err.status === 401) {
        clear();
        return;
      }
      setError(err instanceof Error ? err.message : 'No se pudo cargar la sesión.');
      setStatus('error');
    }
  }, [clear]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    // Cualquier request con 401 fuera del login invalida la sesión local.
    const onUnauthorized = () => clear();
    window.addEventListener('teiba:unauthorized', onUnauthorized);
    return () => window.removeEventListener('teiba:unauthorized', onUnauthorized);
  }, [clear]);

  const login = useCallback(async (correo: string, contrasena: string) => {
    const { data } = await postLogin(correo.trim(), contrasena);
    setUsuario(data.usuario);
    setPerfil(data.perfil);
    setStatus('authenticated');
    setError(null);
    return data;
  }, []);

  const logout = useCallback(async () => {
    try {
      await postLogout();
    } catch {
      // El logout es best-effort: la cookie expira igual y se limpia el estado.
    }
    clear();
  }, [clear]);

  const value = useMemo(
    () => ({ status, usuario, perfil, error, login, logout, refresh }),
    [status, usuario, perfil, error, login, logout, refresh],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider.');
  return ctx;
}
