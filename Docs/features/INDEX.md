---
status: vigente
last_reviewed: 2026-11-09
---

# Registro de features

## Activas

| Fecha | Cambio | Estado | Área | Alcance | Registro | Evidencia |
|---|---|---|---|---|---|---|
| 2026-10-24 | Agente Sage y panel de monitoreo | en-curso | backend | Backend y seed listos; frontend en pausa | [002-agente-sage-panel.md](002-agente-sage-panel.md) | - |
| 2026-10-27 | Roles de demostración y Libro de parques | en-curso | datos | Endpoints read-only de parques + frontend con roles | [003-roles-libro-parques.md](003-roles-libro-parques.md) | criterios 1-2 registrados |
| 2026-10-28 | Bolder artístico del panel Sage | en-curso | frontend | Firma de un solo hilo copper + hardening P0-P2 | [004-sage-bolder.md](004-sage-bolder.md) | critique 24/40, tests 28/28, detect limpio |
| 2026-10-28 | Header simplificado y transecto con identidad | en-curso | frontend | Sin pills/nav/modelo; nodos numerados 01–05 | [005-header-transecto.md](005-header-transecto.md) | tests 32/32, detect limpio |
| 2026-10-28 | Pipeline frontend y pilot SageView | cerrada | frontend | Dirección, estación, bitácora y showcase | [006-pipeline-frontend-sage.md](006-pipeline-frontend-sage.md) | PASS; rating 4/5; tests 32/32; axe 0 |

## Cerradas

| Fecha | Cambio | Estado | Área | Alcance | Registro | Evidencia |
|---|---|---|---|---|---|---|
| 2026-11-09 | Scripts de demo leen `backend/.env` | cerrada | backend | `seed_auth`, `smoke_demo` y `check_model` sin exportar variables a mano | [013-scripts-env.md](013-scripts-env.md) | seed + login/registro reales; suite y ruff verdes |
| 2026-11-09 | Registro público y acceso visual MVP | cerrada | frontend | Alta de ciudadano, `AuthLayout`/`RegisterView`, README y roles demo | [012-registro-auth-mvp.md](012-registro-auth-mvp.md) | criterios 1-7; 57 frontend; 179 backend; UI limpio |
| 2026-11-09 | Login local SQLite + roles admin/operator/user | cerrada | backend | Cookie, bcrypt, RBAC, CSRF, perfil, login/guards/AccountMenu | [007-login-sqlite.md](007-login-sqlite.md) | suite 179 backend + 57 frontend |
| 2026-10-27 | Entrega 3: implantación y consultas | cerrada | datos | Word E3 con scripts, 5 consultas, versiones y anexo | [003-entrega3-implantacion.md](003-entrega3-implantacion.md) | bitácora en la spec |
| 2026-10-27 | Entrega 3 - Implantacion y consultas | cerrada | datos | Pendiente de detallar | [003-entrega3-implantacion.md](003-entrega3-implantacion.md) | - |
| 2026-10-31 | Mantenimientos e incidentes por rol | cerrada | backend | Prioridad, notas, incidentes y RBAC admin/operador; UI admin/operador | [011-mantenimientos-incidentes.md](011-mantenimientos-incidentes.md) | criterios 1-8; 168 backend + 49 frontend; seed 2x; detect limpio |
