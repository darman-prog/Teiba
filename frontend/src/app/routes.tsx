import type { ReactElement } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useRole } from './RoleProvider';
import { SageView } from '../features/agent/SageView';
import { ParkDetail } from '../features/parks/ParkDetail';
import { ParkIndex } from '../features/parks/ParkIndex';
import { Showcase } from '../features/showcase/Showcase';

// Guardia de demo: el usuario que navegue a /sage redirige al libro.
function AdminOnly({ children }: { children: ReactElement }) {
  const { role } = useRole();
  if (role !== 'admin') return <Navigate to="/parques" replace />;
  return children;
}

function RootRedirect() {
  const { role } = useRole();
  return <Navigate to={role === 'admin' ? '/sage' : '/parques'} replace />;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route
        path="/sage"
        element={
          <AdminOnly>
            <SageView />
          </AdminOnly>
        }
      />
      <Route path="/parques" element={<ParkIndex />} />
      <Route path="/parques/:codigo" element={<ParkDetail />} />
      <Route path="/showcase" element={import.meta.env.DEV ? <Showcase /> : <Navigate to="/" replace />} />
      <Route path="*" element={<RootRedirect />} />
    </Routes>
  );
}
