import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import type { DomainRole } from '../types/api';

const ROL_LABEL: Record<DomainRole, string> = {
  administrador: 'Administrador',
  operador_mantenimiento: 'Operador de mantenimiento',
  ciudadano: 'Ciudadano',
};

// Menú de cuenta: nombre, perfil de dominio y logout; reemplaza el switch demo.
export function AccountMenu() {
  const { usuario, perfil, logout } = useAuth();
  const navigate = useNavigate();

  if (!usuario) return null;
  const nombre = perfil?.nombre ?? usuario.correo;
  const rol = perfil ? ROL_LABEL[perfil.rol] : 'Perfil no configurado';

  async function cerrarSesion() {
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <details className="relative">
      <summary className="flex min-h-[44px] cursor-pointer list-none items-center gap-2 rounded-[6px] border border-border bg-surface px-3 text-[13px] font-semibold text-ink md:min-h-0 md:py-1.5">
        <span className="max-w-[160px] truncate">{nombre}</span>
        <span className="hidden text-[12px] font-normal text-ink-2 sm:inline">{rol}</span>
      </summary>
      <div className="absolute right-0 z-40 mt-2 w-64 rounded-[8px] border border-border bg-surface p-2 text-[13px]">
        <p className="truncate px-2 py-1 text-ink-2">{usuario.correo}</p>
        <p className="px-2 py-1 text-[12px] text-ink-2">
          Acceso: <span className="font-mono">{usuario.rol}</span>
          {' · '}Perfil: <span className="font-mono">{perfil?.rol ?? 'sin perfil'}</span>
        </p>
        <button
          type="button"
          onClick={cerrarSesion}
          className="mt-1 flex min-h-[44px] w-full items-center gap-2 rounded-[4px] px-2 text-left font-semibold text-ink hover:bg-neutral-soft"
        >
          <LogOut size={15} strokeWidth={1.5} aria-hidden="true" />
          Cerrar sesión
        </button>
      </div>
    </details>
  );
}
