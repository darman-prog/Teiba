import { useCallback, useEffect, useRef, useState } from 'react';
import { Plus } from 'lucide-react';
import { useAgent } from '../../hooks/useAgent';
import { useSensors } from '../../hooks/useSensors';
import { SensorStrip } from '../sensors/SensorStrip';
import { Composer } from './Composer';
import { ErrorBanner } from './ErrorBanner';
import { FieldLog } from './FieldLog';
import { SignalPath } from './SignalPath';
import { StationStrip } from './StationStrip';
import { Button } from '../../shared/ui/Button';
import { useDocumentTitle } from '../../lib/useDocumentTitle';

// Estación Sage: transecto + bitácora + ruta. 1440: 7/5; 768–1279: tabs; <768: una columna.
export function SageView() {
  const sensors = useSensors();
  const agent = useAgent(sensors.refresh);
  const [draft, setDraft] = useState('');
  const [tab, setTab] = useState<'log' | 'path'>('log');
  const composerRef = useRef<HTMLTextAreaElement>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const selected = agent.messages.find((m) => m.id === agent.selectedId && m.role === 'assistant') ?? null;
  useDocumentTitle('Sage · Teiba');

  // En móvil el composer es fijo: al llegar una respuesta, deja su final por encima.
  useEffect(() => {
    if (agent.loading || agent.messages.length === 0) return;
    const last = agent.messages[agent.messages.length - 1];
    if (last.role !== 'assistant') return;
    requestAnimationFrame(() => {
      const el = logEndRef.current;
      // jsdom no implementa scrollIntoView; el navegador sí.
      if (el && typeof el.scrollIntoView === 'function') el.scrollIntoView({ block: 'end' });
    });
  }, [agent.messages.length, agent.loading]);

  // Tras un error, restaura el borrador para cumplir input preservado.
  useEffect(() => {
    if (agent.error && agent.lastFailed) setDraft((d) => (d === '' ? agent.lastFailed ?? '' : d));
  }, [agent.error, agent.lastFailed]);

  // Precarga la pregunta del sensor y enfoca el composer.
  const askSensor = useCallback((id: string) => {
    setDraft(`¿Cómo está el sensor ${id}?`);
    requestAnimationFrame(() => composerRef.current?.focus());
  }, []);

  const pick = useCallback((q: string) => {
    setDraft(q);
    requestAnimationFrame(() => composerRef.current?.focus());
  }, []);

  const sendDraft = useCallback(() => {
    const q = draft.trim();
    if (q.length < 3 || q.length > 500 || agent.loading) return;
    setDraft('');
    void agent.send(q).then(() => {
      // Si falla, restaura el borrador para reintento con input preservado.
      // useAgent ya guarda lastFailed; aquí no se pisa el estado válido.
    });
  }, [draft, agent]);

  return (
    <div className="flex flex-col gap-3">
      <StationStrip sensors={sensors.items} selected={selected} loading={agent.loading} />
      <div className="hidden md:block">
        <SensorStrip items={sensors.items} loading={sensors.loading} onAsk={askSensor} onRefresh={sensors.refresh} label="Transecto de sensores" />
      </div>
      {sensors.error && (
        <p role="alert" className="rounded-[6px] border border-warn/40 bg-warn-soft px-3 py-2 text-[13px] text-warn">
          No se pudo cargar el transecto: {sensors.error.message}{' '}
          <button type="button" onClick={sensors.refresh} className="font-semibold underline">
            Reintentar
          </button>
        </p>
      )}

      <div className="flex items-center justify-between gap-2">
        <h1 className="font-display text-[20px] font-semibold text-ink">Bitácora de campo</h1>
        <Button
          variant="secondary"
          onClick={() => {
            agent.reset();
            setDraft('');
          }}
        >
          <Plus size={15} strokeWidth={1.5} aria-hidden="true" />
          Nueva consulta
        </Button>
      </div>

      {agent.error && (
        <ErrorBanner error={agent.error} pregunta={agent.lastFailed} onRetry={agent.retry} onDismiss={agent.dismissError} />
      )}

      {/* Tabs solo en tablet 768–1279. */}
      <div className="hidden gap-1 rounded-[6px] border border-border bg-surface p-1 md:flex xl:hidden" role="tablist" aria-label="Vistas de la estación">
        {(['log', 'path'] as const).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={`min-h-[44px] flex-1 rounded-[4px] px-3 py-2 text-[14px] font-semibold ${tab === t ? 'bg-moss text-white' : 'text-ink-2'}`}
          >
            {t === 'log' ? 'Bitácora' : 'Ruta'}
          </button>
        ))}
      </div>

      {/* Desktop ≥1280: 7/5. */}
      <div className="hidden items-start gap-3 xl:grid xl:grid-cols-12">
        <div className="flex flex-col gap-3 xl:col-span-7">
          <FieldLog messages={agent.messages} loading={agent.loading} selectedId={agent.selectedId} onSelect={agent.select} onPick={pick} />
          <Composer ref={composerRef} value={draft} onChange={setDraft} onSend={sendDraft} loading={agent.loading} />
        </div>
        <div className="xl:col-span-5">
          <div className="sticky top-[76px]">
            <SignalPath key={selected?.id ?? 'vacia'} message={selected} />
          </div>
        </div>
      </div>

      {/* Tablet 768–1279: una vista por tab. */}
      <div className="hidden flex-col gap-3 md:flex xl:hidden">
        {tab === 'log' ? (
          <>
            <FieldLog messages={agent.messages} loading={agent.loading} selectedId={agent.selectedId} onSelect={agent.select} onPick={pick} />
            <Composer ref={composerRef} value={draft} onChange={setDraft} onSend={sendDraft} loading={agent.loading} />
          </>
        ) : (
          <SignalPath key={selected?.id ?? 'vacia'} message={selected} />
        )}
      </div>

      {/* Móvil <768: una columna, ruta colapsada y composer fijo con espacio de scroll. */}
      <div className="flex flex-col gap-3 md:hidden">
        <FieldLog messages={agent.messages} loading={agent.loading} selectedId={agent.selectedId} onSelect={agent.select} onPick={pick} />
        <div ref={logEndRef} aria-hidden="true" className="h-px scroll-mb-56" />
        <SensorStrip items={sensors.items} loading={sensors.loading} onAsk={askSensor} onRefresh={sensors.refresh} label="Transecto de sensores móvil" />
        {selected && selected.trazas.length > 0 && <SignalPath key={selected.id} message={selected} />}
        <div aria-hidden="true" className="h-56" />
      </div>
      <div className="fixed inset-x-0 bottom-0 z-20 border-t border-border bg-mineral px-4 pb-[env(safe-area-inset-bottom)] pt-2 md:hidden">
        <div className="mx-auto max-w-6xl">
          <Composer ref={composerRef} value={draft} onChange={setDraft} onSend={sendDraft} loading={agent.loading} />
        </div>
      </div>
    </div>
  );
}
