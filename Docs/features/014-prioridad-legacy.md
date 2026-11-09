---
id: 014
status: cerrada
area: backend
tarea: -
created: 2026-11-09
updated: 2026-11-09
---
# Feature 014 — Tareas antiguas sin `prioridad`

## Objetivo
Evitar el 500 del listado cuando Mongo conserva tareas previas a la feature 011.

## Cambio
- `_item` usa `prioridad: "media"` si el documento no trae el campo.
- `seed_mantenimientos` rellena con `"media"` las tareas antiguas.
- Test de regresión del serializador.

## Criterios
| N.º | Verificable | Comando |
|---|---|---|
| 1 | Serializador tolerante | `cd backend && .\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance_api_item.py -q` |
| 2 | Backfill idempotente | `cd backend && .\.venv\Scripts\python.exe -m app.scripts.seed_mantenimientos` |
| 3 | Suite y lint | `cd backend && .\.venv\Scripts\python.exe -m pytest -q && .\.venv\Scripts\python.exe -m ruff check .` |

## Evidencia
- 10 tareas antiguas actualizadas; `GET /api/mantenimientos` devuelve 18 sin 500.
- 183 tests y `ruff` limpio.

## Rollback
Revertir el commit; no hay migración destructiva ni cambios de contrato.
