import type { AuthUser, PerfilUsuario } from '../types/api';

// Home por perfil de dominio, respetando el rol de acceso y las rutas disponibles.
export function homeForPerfil(
  usuario: AuthUser | null,
  perfil: PerfilUsuario | null,
): string {
  if (!usuario) return '/login';

  if (usuario.rol === 'admin') {
    if (!perfil || perfil.rol === 'administrador') return '/sage';
    if (perfil.rol === 'operador_mantenimiento') return '/mantenimientos';
    return '/parques';
  }

  if (usuario.rol === 'operator') {
    return perfil?.rol === 'operador_mantenimiento' ? '/mantenimientos' : '/perfil-no-configurado';
  }

  // Un user con perfil elevado no puede abrir superficies de admin/operador.
  if (perfil && (perfil.rol === 'administrador' || perfil.rol === 'operador_mantenimiento')) {
    return '/perfil-no-configurado';
  }
  return '/parques';
}

// Fallback cuando todavía no hay perfil de dominio.
export function homeForAccess(usuario: AuthUser | null): string {
  if (!usuario) return '/login';
  if (usuario.rol === 'admin') return '/sage';
  if (usuario.rol === 'operator') return '/mantenimientos';
  return '/parques';
}

// Destino interno seguro para volver tras el login; nunca acepta URLs externas.
export function destinoSeguro(state: unknown): string | null {
  const from = (state as { from?: unknown } | null)?.from;
  if (typeof from !== 'string') return null;
  if (!from.startsWith('/') || from.startsWith('//') || from === '/login') return null;
  return from;
}
