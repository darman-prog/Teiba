import { Loader2 } from 'lucide-react';
import { COPY } from '../../lib/copy';

// Carga de la consulta: role=status + aria-busy, respeta reduced-motion por CSS.
export function LoadingState() {
  return (
    <div role="status" aria-busy="true" aria-label={COPY.loadingTitle} className="flex items-start gap-3 rounded-[8px] border border-border bg-surface p-4">
      <Loader2 size={18} strokeWidth={1.5} aria-hidden="true" className="mt-0.5 animate-spin text-moss" />
      <div>
        <p className="text-[14px] font-semibold">{COPY.loadingTitle}</p>
        <p className="text-[13px] text-ink-2">{COPY.loadingBody}</p>
      </div>
    </div>
  );
}
