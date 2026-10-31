---
id: 011
status: en-curso
area: backend
tarea: B-001
created: 2026-10-31
updated: 2026-10-31
---
# Feature 011 — Mantenimientos e incidentes por rol

> Ciclo incidente → tarea asignada → ejecución → cierre/reapertura, con prioridad,
> notas y RBAC para administrador y operador de mantenimiento.
## Objetivo
Que el administrador asigne y controle tareas de mantenimiento y que el operador
ejecute solo las suyas, con trazabilidad de cierre y reapertura.

## Contexto
`mantenimientos` e `incidentes` existen en el modelo pero el panel no los usa.
Auth expone hoy `admin`/`user`; el operador requiere un rol de acceso y un perfil
Mongo (`usuarios`) que aporte el ObjectId de `responsable_id`. Mongo corre sin
transacciones: el estado del incidente se actualiza con una acción explícita.

## Alcance
| Incluye | Excluye |
|---|---|
| Campos `prioridad`, `nota_cierre`, `nota_reapertura`, `fecha_reapertura`, `incidente_id`; endpoints de mantenimientos, operadores, incidentes y elementos; vistas admin/operador; seed; tests; docs | Registro, reset, 2FA, notificaciones, evidencias, Kanban, historial completo, CRUD de incidentes o inventario |

## Criterios de aceptación
| N.º | Criterio verificable | Comando | Evidencia |
|---|---|---|---|
| 1 | Dominio de estados y permisos | `cd backend && .\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance.py -q` | exit 0 |
| 2 | Repositorios e índices | `cd backend && .\.venv\Scripts\python.exe -m pytest tests/integration/test_maintenance_repository.py -q` | exit 0 |
| 3 | Contrato HTTP y RBAC | `cd backend && .\.venv\Scripts\python.exe -m pytest tests/api/test_maintenance_api.py tests/api/test_incidents_api.py -q` | exit 0 |
| 4 | Seed idempotente | `cd backend && .\.venv\Scripts\python.exe -m app.scripts.seed_mantenimientos` dos veces | mismos conteos |
| 5 | Suite backend | `cd backend && .\.venv\Scripts\python.exe -m pytest -q && .\.venv\Scripts\python.exe -m ruff check .` | exit 0 |
| 6 | Frontend compila y prueba | `cd frontend && npm run typecheck && npm run lint && npm run test -- --run && npm run build` | exit 0 |
| 7 | Accesibilidad | `cd frontend && npm run test -- --run src/features/maintenance` | axe 0 |
| 8 | Tokens y detector | `cd frontend && npm run check:ui && npm run detect:ui` | exit 0 / `[]` |

## Pasos
1. Contrato y modelo — `docs: definir mantenimientos e incidentes`
2. Dominio y tests — `feat: implementar reglas de mantenimientos`
3. Repositorios e índices — `feat: persistir mantenimientos e incidentes`
4. API y RBAC — `feat: exponer mantenimientos por rol`
5. Seed y datos demo — `feat: sembrar tareas e incidentes`
6. Frontend admin — `feat: añadir vista de mantenimientos del administrador`
7. Frontend operador — `feat: añadir mis tareas al operador`
8. Cierre visual y docs — `docs: cerrar mantenimientos e incidentes`

## Bitácora
| Criterio | Fecha | Comando | Exit | Commit |
|---|---|---|---|---|
| 1 | 2026-10-31 | cd backend && .\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance.py -q | 0 | f8def0a |

## Rollback
Revertir los commits de `feat/mantenimientos`; no hay migración de datos existente.
Los documentos nuevos usan defaults y el seed es idempotente.

## Cierre
- Fila resumen del changelog: "Mantenimientos con prioridad, notas, incidentes y RBAC admin/operador".
- Decisión de arquitectura: no aplica; el estado del incidente es manual por falta de transacciones en Mongo standalone.
