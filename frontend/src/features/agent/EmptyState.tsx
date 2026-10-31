import { NotebookPen } from 'lucide-react';
import { SUGERENCIAS_SAGE, COPY } from '../../lib/copy';
import { Button } from '../../shared/ui/Button';

// Estado vacío de la bitácora con 3 sugerencias del brief.
export function EmptyState({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-[8px] border border-dashed border-border bg-surface p-4">
      <span aria-hidden="true" className="grid size-9 place-items-center rounded-[6px] border border-border bg-mineral text-moss">
        <NotebookPen size={18} strokeWidth={1.5} />
      </span>
      <div>
        <p className="font-display text-[15px] font-semibold">{COPY.emptyTitle}</p>
        <p className="mt-1 max-w-prose text-[14px] text-ink-2">{COPY.emptyBody}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {SUGERENCIAS_SAGE.map((s) => (
          <Button key={s} variant="secondary" onClick={() => onPick(s)}>
            {s}
          </Button>
        ))}
      </div>
    </div>
  );
}
