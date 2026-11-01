import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Activity, FlaskConical } from 'lucide-react';
import { useAuth } from './AuthProvider';
import { AccountMenu } from './AccountMenu';
import { isMockEnabled } from '../api/client';
import { homeForPerfil } from '../lib/navigation';

// Station bar: marca, aviso de perfil y cuenta de la sesión.
export function AppShell({ children }: { children: ReactNode }) {
  const { status, usuario, perfil } = useAuth();
  const mock = isMockEnabled();
  const home = usuario ? homeForPerfil(usuario, perfil) : '/login';

  return (
    <div className="flex min-h-dvh flex-col bg-mineral text-ink">
      <a
        href="#contenido"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-[6px] focus:bg-surface focus:px-3 focus:py-2 focus:text-[14px] focus:font-semibold"
      >
        Saltar al contenido principal
      </a>
      <header className="sticky top-0 z-30 border-b border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2.5">
          <Link to={home} className="flex items-center gap-2.5">
            <span aria-hidden="true" className="grid size-8 place-items-center rounded-[6px] border border-moss bg-moss text-white">
              <Activity size={18} strokeWidth={1.5} />
            </span>
            <span className="leading-tight">
              <span className="block font-display text-[15px] font-semibold tracking-wide">Teiba</span>
              <span className="block text-[12px] text-ink-2">Estación de campo — hilos de datos, parques vivos</span>
            </span>
          </Link>
          <div className="ml-auto flex flex-wrap items-center gap-2">
            {mock && (
              <span className="flex items-center gap-1 rounded-[4px] border border-signal bg-[#FDF6E7] px-2 py-1 text-[12px] font-semibold text-warn">
                <FlaskConical size={14} strokeWidth={1.5} aria-hidden="true" /> Datos demo
              </span>
            )}
            {status === 'authenticated' && !perfil && (
              <span className="rounded-[4px] border border-warn/40 bg-warn-soft px-2 py-1 text-[12px] font-semibold text-warn">
                Perfil no configurado
              </span>
            )}
            {status === 'authenticated' && <AccountMenu />}
          </div>
        </div>
      </header>
      <main id="contenido" className="mx-auto w-full max-w-6xl flex-1 px-4 pb-24 pt-4 md:pb-10">
        {children}
      </main>
      <footer className="border-t border-border bg-surface">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-2 px-4 py-3 text-[12px] text-ink-2">
          <span className="font-display font-semibold uppercase tracking-[0.08em]">Teiba · Estación de campo</span>
          <span aria-hidden="true">—</span>
          <span>Demo local con sesión · la key vive en el backend</span>
        </div>
      </footer>
    </div>
  );
}
