import type { ChatMessage } from '../../hooks/useAgent';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';
import { LogEntry } from './LogEntry';

// Bitácora de campo: role=log + aria-live polite para la respuesta nueva.
export function FieldLog({
  messages,
  loading,
  selectedId,
  onSelect,
  onPick,
}: {
  messages: ChatMessage[];
  loading: boolean;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onPick: (q: string) => void;
}) {
  if (messages.length === 0 && !loading) return <EmptyState onPick={onPick} />;
  // El live vive solo en la última respuesta: el contenedor no re-anuncia el historial.
  const lastAssistantId = [...messages].reverse().find((m) => m.role === 'assistant' && !m.failed)?.id;
  return (
    <div role="log" aria-label="Bitácora de Sage" className="flex flex-col">
      {messages.map((m, i) => (
        <LogEntry key={m.id} message={m} index={i} selected={selectedId === m.id} onSelect={onSelect} live={m.id === lastAssistantId} />
      ))}
      {loading && <LoadingState />}
    </div>
  );
}
