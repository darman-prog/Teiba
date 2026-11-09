---
id: 013
status: cerrada
area: backend
tarea: -
created: 2026-11-09
updated: 2026-11-09
---
# Feature 013 — Scripts de demo leen `backend/.env`

## Objetivo
Que `seed_auth`, `smoke_demo` y `check_model` usen las credenciales del `.env`
sin exportarlas a mano en la shell.

## Cambio
- `Settings` resuelve `backend/.env` con ruta absoluta, sin depender del CWD.
- `cargar_env_local()` carga el `.env` en `os.environ` sin pisar variables ya
  exportadas; lo usan los tres scripts.
- No cambia el contrato HTTP ni el esquema de datos.

## Criterios
| N.º | Verificable | Comando |
|---|---|---|
| 1 | `seed_auth` lee las claves del `.env` | `cd backend && .\.venv\Scripts\python.exe -m app.scripts.seed_auth` |
| 2 | Suite y lint | `cd backend && .\.venv\Scripts\python.exe -m pytest -q && .\.venv\Scripts\python.exe -m ruff check .` |

## Evidencia
- `seed_auth` creó `admin`, `operator` y `user` usando `AUTH_*_PASSWORD` del `.env`.
- Login admin y registro público verificados contra la API real con Mongo.
- Suite completa en verde; `ruff` limpio.

## Rollback
Revertir el commit del fix; no hay migración ni datos nuevos.
