import { Search } from 'lucide-react';

// Buscador con icono y label real para el libro.
export function SearchInput({
  id,
  label,
  value,
  onChange,
  placeholder,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="field-label">
        {label}
      </label>
      <div className="relative">
        <Search size={16} strokeWidth={1.5} aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-2" />
        <input
          id={id}
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-[6px] border border-border bg-surface py-2.5 pl-9 pr-3 text-[14px] text-ink placeholder:text-ink-2/70"
        />
      </div>
    </div>
  );
}
