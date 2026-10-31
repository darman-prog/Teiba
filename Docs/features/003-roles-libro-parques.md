---
id: 003
status: en-curso
area: datos
tarea: -
created: 2026-10-27
updated: 2026-10-27
---
# Feature 003 — Roles de demostración y Libro de parques

## Objetivo
App con dos superficies: el administrador usa la estación Sage y el usuario consulta el Libro de parques. Los roles son un switch de demo (sin auth); el libro se alimenta de un endpoint read-only sobre `parques` y `sectores` con indicaciones derivadas.

## Contexto
El backend no tiene autenticación y `usuarios` no guarda contraseñas: un login real es otra feature. `GET /api/parques` no existe; la ficha del libro necesita `parques` + `sectores` e indicaciones que no están en el modelo, así que se derivan de `estado_general`, `tipo_parque` y `zona_riesgo` en el dominio.

## Alcance
| Incluye | Excluye |
|---|---|
| Endpoints `GET /api/parques` y `GET /api/parques/{codigo}`, dominio de indicaciones, rutas `/sage` y `/parques`, switch de demo, libro con índice/ficha | Login real, auth, RBAC en backend, CRUD, mapas, telemetría en el libro, Sage para el usuario |

## Criterios de aceptación
| N.º | Criterio verificable | Comando | Evidencia |
|---|---|---|---|
| 1 | Indicaciones derivadas sin duplicados | `cd backend && .venv\Scripts\python.exe -m pytest tests/unit/test_park_indications.py -q` | exit 0 |
| 2 | Libro: lista, ficha, 404/422/503 | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_parks_api.py -q` | exit 0 |
| 3 | Backend probado y lint limpio | `cd backend && .venv\Scripts\python.exe -m pytest -q && .venv\Scripts\python.exe -m ruff check .` | exit 0 |
| 4 | Frontend compila, pasa lint y tests | `cd frontend && npm run typecheck && npm run lint && npm run test -- --run && npm run build` | exit 0 |
| 5 | Roles demo: admin ve Sage, usuario solo el libro | `cd frontend && npm run test -- --run tests/roles` | exit 0 |
| 6 | Accesibilidad sin violaciones automáticas | `cd frontend && npm run test -- --run tests/a11y` | exit 0 |
| 7 | Sin secretos en el diff | `git diff` revisado | sin `.env`, keys ni artefactos |

## Pasos
1. Backend: dominio, repositorio, endpoints y tests — `feat: exponer parques y sectores para el libro`
2. Frontend: shell, rutas, switch de demo y libro — `feat: añadir roles de demostración y libro de parques`
3. Frontend: panel Sage sobre el mundo “Estación de campo” — `feat: implementar la estación Sage en React`
4. Cierre: `detect`/axe, docs y bitácora — `docs: cerrar roles y libro de parques`

## Bitácora
| Criterio | Fecha | Comando | Exit | Commit |
|---|---|---|---|---|
| 1 | 2026-10-27 | cd backend && .venv\Scripts\python.exe -m pytest tests/unit/test_park_indications.py -q | 0 | - |
| 2 | 2026-10-27 | cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_parks_api.py -q | 0 | - |
| 3 | 2026-10-27 | cd backend && .venv\Scripts\python.exe -m pytest -q (86 passed) y ruff check . | 0 | - |
| 4 | 2026-10-27 | cd frontend && npm run typecheck, lint, test -- --run (26/26), build | 0 | - |
| 5 | 2026-10-27 | cd frontend && npm run test -- --run (incluye src/app/Roles.test.tsx) | 0 | - |
| 6 | 2026-10-27 | cd frontend && npm run test -- --run (incluye src/app/App.axe.test.tsx) | 0 | - |
| 7 | 2026-10-27 | git diff revisado: sin .env, keys ni artefactos | 0 | - |

## Rollback
Revertir `backend/app/api/parks.py`, `backend/app/domain/parks.py`, DTOs/puertos y tests; quitar el router de `main.py`. La base `teiba_db` no se toca.

## Cierre
- Fila resumen del changelog: "Libro de parques con endpoints read-only, roles de demo y panel Sage en React".
- Sin ADR: no hay decisión de auth; el switch es demo.
