import type { ReactNode } from 'react';

interface AuthLayoutProps {
  kicker: string;
  title: string;
  intro: string;
  children: ReactNode;
  footer?: ReactNode;
}

const ROLES = [
  {
    numero: '01',
    nombre: 'Ciudadano',
    detalle: 'Consulta el libro de parques y sigue el estado de los sensores.',
  },
  {
    numero: '02',
    nombre: 'Operador de mantenimiento',
    detalle: 'Ejecuta las tareas que le asigna el administrador.',
  },
  {
    numero: '03',
    nombre: 'Administrador',
    detalle: 'Opera la estación Sage y asigna tareas en los parques.',
  },
];

// Marco de acceso: identidad de estación a la izquierda, formulario a la derecha.
export function AuthLayout({ kicker, title, intro, children, footer }: AuthLayoutProps) {
  return (
    <div className="mx-auto mt-3 grid max-w-5xl gap-4 md:mt-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
      <aside className="relative overflow-hidden rounded-[8px] border border-moss-deep bg-moss-deep p-5 text-white lg:p-7">
        <span aria-hidden="true" className="absolute inset-y-0 left-0 w-[3px] bg-copper" />
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-white/70">
          Teiba · Estación de campo
        </p>
        <p className="mt-4 font-display text-[26px] font-semibold leading-[1.15]">
          Hilos de datos,
          <br />
          parques vivos.
        </p>
        <p className="mt-3 max-w-sm text-[13px] leading-relaxed text-white/75">
          Sensores, incidentes y tareas de mantenimiento en una sola traza. La sesión vive en una
          cookie HttpOnly: ningún token toca el navegador.
        </p>

        <ol className="mt-6 space-y-3 border-t border-white/15 pt-5">
          {ROLES.map((rol) => (
            <li key={rol.numero} className="grid grid-cols-[2rem_1fr] gap-2">
              <span className="pt-0.5 font-mono text-[12px] font-semibold text-signal" aria-hidden="true">
                {rol.numero}
              </span>
              <span>
                <span className="block text-[13px] font-semibold text-white">{rol.nombre}</span>
                <span className="block text-[12px] leading-snug text-white/65">{rol.detalle}</span>
              </span>
            </li>
          ))}
        </ol>

        <p className="mt-6 font-mono text-[11px] text-white/70">
          Cookie HttpOnly · CSRF por Origin · RBAC en servidor
        </p>
      </aside>

      <section
        aria-labelledby="auth-title"
        className="rounded-[8px] border border-border bg-surface p-5 lg:p-7"
      >
        <p className="field-label">{kicker}</p>
        <h1 id="auth-title" className="mt-1 font-display text-[24px] font-semibold text-ink">
          {title}
        </h1>
        <p className="mt-1 max-w-md text-[13px] leading-relaxed text-ink-2">{intro}</p>
        <div className="mt-5">{children}</div>
        {footer && <div className="mt-5 border-t border-border pt-4 text-[13px] text-ink-2">{footer}</div>}
      </section>
    </div>
  );
}
