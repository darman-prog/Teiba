import type { ReactElement } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { LoginView } from '../features/auth/LoginView';
import { SageView } from '../features/agent/SageView';
import { MaintenanceView } from '../features/maintenance/MaintenanceView';
import { ParkDetail } from '../features/parks/ParkDetail';
import { ParkIndex } from '../features/parks/ParkIndex';
import { Showcase } from '../features/showcase/Showcase';
import { Button } from '../shared/ui/Button';
import { destinoSeguro, homeForPerfil } from '../lib/navigation';

function AuthLoading() {
  return (
    <p role="status" className="rounded-[6px] border border-border bg-surface px-3 py-2 text-[13px] text-ink-2">
      Comprobando sesión…
    </p>
  );
}

function AuthError() {
  const { error, refresh } = useAuth();
  return (
    <div role="alert" className="rounded-[8px] border border-danger/40 bg-danger-soft p-4">
      <p className="text-[14px] font-semibold text-danger">No se pudo comprobar la sesión.</p>
      <p className="mt-1 text-[13px] text-ink">{error ?? 'Error de red con la API.'}</p>
      <div className="mt-3">
        <Button onClick={() => void refresh()}>Reintentar</Button>
      </div>
    </div>
  );
}

// Ruta pública: si ya hay sesión, manda a su home.
function PublicOnly({ children }: { children: ReactElement }) {
  const { status, usuario, perfil } = useAuth();
  const location = useLocation();
  if (status === 'loading') return <AuthLoading />;
  if (status === 'error') return <AuthError />;
  if (status === 'authenticated') {
    // Respeta el destino que RequireAuth guardó antes de mandar a login.
    return <Navigate to={destinoSeguro(location.state) ?? homeForPerfil(usuario, perfil)} replace />;
  }
  return children;
}

// Ruta autenticada: conserva el destino para volver después del login.
function RequireAuth({ children }: { children: ReactElement }) {
  const { status } = useAuth();
  const location = useLocation();
  if (status === 'loading') return <AuthLoading />;
  if (status === 'error') return <AuthError />;
  if (status === 'anonymous') {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: `${location.pathname}${location.search}` }}
      />
    );
  }
  return children;
}

function RequireAdmin({ children }: { children: ReactElement }) {
  const { usuario, perfil } = useAuth();
  if (usuario?.rol !== 'admin') return <Navigate to={homeForPerfil(usuario, perfil)} replace />;
  return children;
}

// Admin y operador solo entran con un perfil de dominio que corresponda.
function RequireMantenimientos({ children }: { children: ReactElement }) {
  const { usuario, perfil } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  if (usuario.rol === 'admin') {
    if (perfil?.rol === 'administrador' || perfil?.rol === 'operador_mantenimiento') return children;
    return <Navigate to="/perfil-no-configurado" replace />;
  }
  if (usuario.rol === 'operator') {
    if (perfil?.rol === 'operador_mantenimiento') return children;
    return <Navigate to="/perfil-no-configurado" replace />;
  }
  return <Navigate to={homeForPerfil(usuario, perfil)} replace />;
}

function RootRedirect() {
  const { status, usuario, perfil } = useAuth();
  if (status === 'loading') return <AuthLoading />;
  if (status === 'error') return <AuthError />;
  if (!usuario) return <Navigate to="/login" replace />;
  return <Navigate to={homeForPerfil(usuario, perfil)} replace />;
}

function ProfileNoConfigurado() {
  const { usuario, perfil, logout } = useAuth();
  const navigate = useNavigate();

  async function cerrarSesion() {
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <section className="mx-auto mt-6 max-w-xl rounded-[8px] border border-border bg-surface p-5">
      <p className="field-label">Perfil pendiente</p>
      <h1 className="mt-1 font-display text-[20px] font-semibold text-ink">Perfil no configurado</h1>
      <p className="mt-2 text-[14px] text-ink-2">
        La sesión de <span className="font-mono">{usuario?.correo}</span> no tiene un perfil de
        dominio en Mongo. Ejecuta el seed de mantenimientos para crear los perfiles demo.
      </p>
      <p className="mt-2 text-[13px] text-ink-2">
        Rol de acceso: <span className="font-mono">{usuario?.rol ?? '—'}</span>
        {' · '}Perfil: <span className="font-mono">{perfil?.rol ?? 'sin perfil'}</span>
      </p>
      <div className="mt-4">
        <Button variant="secondary" onClick={cerrarSesion}>
          Cerrar sesión
        </Button>
      </div>
    </section>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnly>
            <LoginView />
          </PublicOnly>
        }
      />
      <Route
        path="/perfil-no-configurado"
        element={
          <RequireAuth>
            <ProfileNoConfigurado />
          </RequireAuth>
        }
      />
      <Route
        path="/sage"
        element={
          <RequireAuth>
            <RequireAdmin>
              <SageView />
            </RequireAdmin>
          </RequireAuth>
        }
      />
      <Route
        path="/mantenimientos"
        element={
          <RequireAuth>
            <RequireMantenimientos>
              <MaintenanceView />
            </RequireMantenimientos>
          </RequireAuth>
        }
      />
      <Route
        path="/parques"
        element={
          <RequireAuth>
            <ParkIndex />
          </RequireAuth>
        }
      />
      <Route
        path="/parques/:codigo"
        element={
          <RequireAuth>
            <ParkDetail />
          </RequireAuth>
        }
      />
      <Route
        path="/showcase"
        element={
          import.meta.env.DEV ? (
            <RequireAuth>
              <Showcase />
            </RequireAuth>
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route path="/" element={<RootRedirect />} />
      <Route path="*" element={<RootRedirect />} />
    </Routes>
  );
}
