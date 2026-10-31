import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';

export type DemoRole = 'admin' | 'user';
const KEY = 'teiba-role';

interface RoleCtx {
  role: DemoRole;
  setRole: (r: DemoRole) => void;
}

const Ctx = createContext<RoleCtx>({ role: 'admin', setRole: () => {} });

// Rol de demo sin auth: persiste en sessionStorage, default admin.
export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<DemoRole>(() => {
    try {
      const v = sessionStorage.getItem(KEY);
      return v === 'user' ? 'user' : 'admin';
    } catch {
      return 'admin';
    }
  });

  useEffect(() => {
    try {
      sessionStorage.setItem(KEY, role);
    } catch {
      // sessionStorage no disponible: el rol vive solo en memoria.
    }
  }, [role]);

  const setRole = useCallback((r: DemoRole) => setRoleState(r), []);
  return <Ctx.Provider value={{ role, setRole }}>{children}</Ctx.Provider>;
}

export function useRole(): RoleCtx {
  return useContext(Ctx);
}
