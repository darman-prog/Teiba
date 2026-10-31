// Formato de fechas, números y antigüedad para la estación.
export function formatFechaCorta(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

export function formatAntiguedad(min: number | null | undefined): string {
  if (min == null) return 'sin dato';
  if (min < 1) return 'ahora mismo';
  if (min < 60) return `hace ${Math.round(min)} min`;
  const h = min / 60;
  if (h < 24) return `hace ${h.toFixed(h < 10 ? 1 : 0)} h`;
  return `hace ${Math.round(h / 24)} d`;
}

export function formatNumero(n: number | null | undefined, digitos = 1): string {
  if (n == null || Number.isNaN(n)) return '—';
  return n.toFixed(digitos);
}

export function formatArea(m2: number | null | undefined): string {
  if (m2 == null) return '—';
  return `${new Intl.NumberFormat('es-CO').format(m2)} m²`;
}
