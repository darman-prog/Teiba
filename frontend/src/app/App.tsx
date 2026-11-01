import { AppShell } from './AppShell';
import { AuthProvider } from './AuthProvider';
import { AppRoutes } from './routes';

// Raíz de la SPA: sesión + caparazón + rutas.
export default function App() {
  return (
    <AuthProvider>
      <AppShell>
        <AppRoutes />
      </AppShell>
    </AuthProvider>
  );
}
