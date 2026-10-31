import { AppShell } from './AppShell';
import { RoleProvider } from './RoleProvider';
import { AppRoutes } from './routes';

// Raíz de la SPA: proveedor de rol demo + caparazón + rutas.
export default function App() {
  return (
    <RoleProvider>
      <AppShell>
        <AppRoutes />
      </AppShell>
    </RoleProvider>
  );
}
