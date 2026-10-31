import { forwardRef, useId } from 'react';
import { SendHorizonal } from 'lucide-react';
import { COPY } from '../../lib/copy';

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  loading: boolean;
}

// Composer controlado: Enter envía, Shift+Enter salta, contador 0/500, IME seguro.
export const Composer = forwardRef<HTMLTextAreaElement, Props>(function Composer({ value, onChange, onSend, loading }: Props, ref) {
  const len = value.length;
  const invalida = len < 3 || len > 500;
  // useId evita IDs duplicados cuando la vista monta varias copias del composer.
  const uid = useId();
  const inputId = `sage-pregunta-${uid}`;
  const counterId = `sage-contador-${uid}`;

  function enviar() {
    if (invalida || loading) return;
    onSend();
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        enviar();
      }}
      className="rounded-[8px] border border-border bg-surface p-3"
    >
      <label htmlFor={inputId} className="field-label">
        {COPY.composerLabel}
      </label>
      <textarea
        id={inputId}
        ref={ref}
        rows={2}
        value={value}
        maxLength={500}
        disabled={loading}
        aria-describedby={counterId}
        placeholder="Ej. ¿Cómo está el suelo del Sector Norte?"
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          // IME seguro: no enviar mientras el sistema compone el carácter.
          const composing = (e.nativeEvent as unknown as { isComposing?: boolean }).isComposing;
          const atajo = (e.metaKey || e.ctrlKey) && e.key === 'Enter';
          if (((e.key === 'Enter' && !e.shiftKey) || atajo) && !composing) {
            e.preventDefault();
            enviar();
          }
        }}
        className="mt-1.5 w-full resize-y rounded-[6px] border border-border bg-mineral/40 px-3 py-2 text-[14px] text-ink placeholder:text-ink-2/70 disabled:opacity-60"
      />
      <div className="mt-2 flex items-center justify-between gap-2">
        <span className="text-[12px] text-ink-2">{COPY.composerHint}</span>
        <span className="flex items-center gap-2">
          <span id={counterId} className="font-mono text-[12px] text-ink-2">
            {len}/500
          </span>
          <button
            type="submit"
            disabled={loading || invalida}
            className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-1.5 rounded-[6px] bg-moss px-4 text-[14px] font-semibold text-white transition-[background-color,scale] duration-150 ease-out hover:bg-moss-deep motion-safe:enabled:active:scale-[0.96] disabled:bg-border disabled:text-ink-2"
          >
            <SendHorizonal size={16} strokeWidth={1.5} aria-hidden="true" />
            Enviar
          </button>
        </span>
      </div>
    </form>
  );
});
