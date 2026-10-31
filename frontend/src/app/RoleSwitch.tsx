import { useRole } from './RoleProvider';
import { cn } from '../lib/cn';

// Switch visible etiquetado "Demo": admin ve la estación, user solo el libro.
export function RoleSwitch() {
  const { role, setRole } = useRole();
  return (
    <div className="flex items-center gap-2" role="group" aria-label="Rol de demostración">
      <span className="field-label" id="demo-label">
        Demo
      </span>
      <div className="flex rounded-[6px] border border-border bg-surface p-0.5" role="group" aria-labelledby="demo-label">
        {(['admin', 'user'] as const).map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRole(r)}
            aria-pressed={role === r}
            className={cn(
              'min-h-[44px] rounded-[4px] px-3 text-[14px] font-semibold transition-colors md:min-h-0 md:px-2.5 md:py-1',
              role === r ? 'bg-moss text-white' : 'text-ink-2 hover:text-ink',
            )}
          >
            {r === 'admin' ? 'Admin' : 'Usuario'}
          </button>
        ))}
      </div>
    </div>
  );
}
