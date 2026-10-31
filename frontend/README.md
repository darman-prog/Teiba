# Teiba · Sage — Frontend

Estación de campo (React 19 + Vite 8 + TypeScript 6 + Tailwind 4) para el panel de
operaciones de parques y el Libro de parques. El agente Sage responde en lenguaje
natural; cada respuesta guarda su ruta de señales con herramientas verificables.

## Roles de demo (sin auth)

- `admin` ve la estación Sage (`/sage`); `user` solo el Libro (`/parques`).
- Switch visible etiquetado “Demo”, persistido en `sessionStorage` (`teiba-role`), default `admin`.
- `/` redirige según rol; `/sage` con rol `user` redirige a `/parques`.

## Rutas

| Ruta | Quién | Qué |
|---|---|---|
| `/` | — | Redirige según rol |
| `/sage` | admin | Transecto + bitácora + ruta de señales |
| `/parques` | todos | Índice con búsqueda y filtros |
| `/parques/:codigo` | todos | Ficha con sectores e indicaciones |

## Arranque

```powershell
npm install
copy ..\.env.example .env  # o crea .env con VITE_API_URL y VITE_USE_MOCKS
npm run dev
```

Variables (`frontend/.env.example`):

- `VITE_API_URL` — base del backend, default `http://127.0.0.1:8000`.
- `VITE_USE_MOCKS=true` — fixtures locales idénticas al contrato + badge “Modo demo”.

El backend debe correr en `127.0.0.1:8000` con Mongo y `OPENCODE_API_KEY`.
Sin API key en el frontend: vive solo en `backend/.env`.

## Sistema visual

“Estación de campo”: mineral `#F1F4EF`, tinta `#16201B`, moss `#24513E`,
copper `#A65A3A` para hilos, chlorophyll `#6FA84A` solo en nodos/líneas.
Overpass 600 (etiquetas), Public Sans (cuerpo), Spline Sans Mono (datos).
Radios 4–8px, bordes 1px, sin glassmorphism, foco visible con moss.

## Estructura

```text
src/
├── app/        App, AppShell, routes, RoleProvider, RoleSwitch
├── api/        client, health, sensors, agent, parks, errors, mocks
├── types/      DTOs espejo del contrato (snake_case)
├── hooks/      useHealth, useSensors, useAgent, useParques, useParque
├── features/
│   ├── sensors/  SensorStrip, SensorCard, StatusTag
│   ├── agent/    SageView, FieldLog, LogEntry, Composer, SignalPath, SignalNode, SignalDetail, ErrorBanner, EmptyState, LoadingState
│   └── parks/    ParkIndex, ParkCard, ParkFilters, ParkDetail, ParkFacts, SectorList, IndicationList
├── shared/ui/  Button, Chip, Surface, FieldLabel, SearchInput
├── lib/        cn, format, copy
└── test/       setup, fixtures
```

## Scripts

```powershell
npm run typecheck   # tsc -b
npm run lint        # oxlint
npm run test -- --run
npm run build
npm run detect:ui   # detector Impeccable sobre frontend/src
```
