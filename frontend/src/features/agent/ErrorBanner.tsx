import { useState } from 'react';
import { AlertTriangle, Check, Copy } from 'lucide-react';
import { ApiError } from '../../api/errors';
import { mensajePorCodigo, COPY } from '../../lib/copy';
import { Button } from '../../shared/ui/Button';

// Banner de error con role=alert, traceId, copiar, reintentar/descartar.
export function ErrorBanner({
  error,
  pregunta,
  onRetry,
  onDismiss,
}: {
  error: ApiError;
  pregunta: string | null;
  onRetry: () => void;
  onDismiss: () => void;
}) {
  const [copied, setCopied] = useState(false);

  // Copia el traceId al portapapeles con fallback de selección.
  async function copiar() {
    if (!error.traceId) return;
    try {
      await navigator.clipboard.writeText(error.traceId);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div role="alert" className="rounded-[8px] border border-danger/40 bg-danger-soft p-4">
      <p className="flex items-center gap-2 text-[14px] font-semibold text-danger">
        <AlertTriangle size={16} strokeWidth={1.5} aria-hidden="true" />
        {mensajePorCodigo(error.code)}
      </p>
      {pregunta && <p className="mt-1 text-[13px] text-ink">Pregunta conservada: “{pregunta}”</p>}
      {error.retryAfter && <p className="mt-1 text-[13px] text-ink">Reintenta en {error.retryAfter} s.</p>}
      {error.traceId && (
        <p className="mt-2 flex flex-wrap items-center gap-2 font-mono text-[12px] text-ink">
          <span>
            traceId: <span data-testid="trace-id">{error.traceId}</span>
          </span>
          <button
            type="button"
            onClick={copiar}
            className="inline-flex min-h-[44px] items-center gap-1 rounded-[4px] border border-danger/40 bg-surface px-2 text-[12px] font-semibold text-danger md:min-h-0 md:py-1"
          >
            {copied ? <Check size={13} strokeWidth={1.5} aria-hidden="true" /> : <Copy size={13} strokeWidth={1.5} aria-hidden="true" />}
            {copied ? COPY.errorCopied : COPY.errorCopy}
          </button>
        </p>
      )}
      <div className="mt-3 flex flex-wrap gap-2">
        <Button variant="primary" onClick={onRetry}>
          {COPY.errorRetry}
        </Button>
        <Button variant="secondary" onClick={onDismiss}>
          {COPY.errorDiscard}
        </Button>
      </div>
    </div>
  );
}
