# 005 — Header simplificado y transecto con identidad

Limpiar el header del panel y dar a las tarjetas el lenguaje de riel de estación.
Alcance: `AppShell.tsx`, `LogEntry.tsx`, `SensorCard.tsx`, `SensorStrip.tsx`.
Excluye: libro, footer, backend, roles.

## Criterios

1. Header sin pills, sin nav y marca “Teiba” — `Select-String` sin coincidencias
2. Respuesta sin modelo — `Select-String 'meta\.modelo' frontend/src/features/agent/LogEntry.tsx` vacío
3. `npm run typecheck`, `lint`, `test -- --run`, `build` exit 0
4. `detect frontend/src` exit 0 o ignores justificados

## Bitácora

| Fecha | Comando | Exit |
|---|---|---|
| 2026-10-28 | `npm run typecheck`, `lint`, `test -- --run` (32/32), `build` | 0 |
| 2026-10-28 | `detect frontend/src` (`[]`) | 0 |
