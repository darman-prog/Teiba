---
id: 007
status: borrador
area: backend
tarea: -
created: 2026-10-31
updated: 2026-10-31
---
# Feature 007 — Login local con SQLite y roles admin/user

> Backend implementado en `feat/auth-sqlite-backend`; el frontend se acoplará luego.

## Objetivo
Permitir login real con dos cuentas, sesión por cookie y RBAC server-side,
manteniendo MongoDB para los datos de parques, sensores y lecturas.

## Alcance
| Incluye | Excluye |
|---|---|
| SQLite users/sessions, bcrypt, login/logout/me, cookie segura, RBAC, CSRF, rate limit, tests, ADR/docs | Registro, reset, 2FA, OAuth, JWT, multi-worker, frontend (fase posterior) |

## Criterios de aceptación
| N.º | Criterio verificable | Comando |
|---|---|---|
| 1 | Migración y seed SQLite idempotentes | `cd backend && .venv\Scripts\python.exe -m pytest tests/integration/test_sqlite_auth_repository.py -q` |
| 2 | Login/cookie/401/429/logout/me | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py -q` |
| 3 | RBAC 401/403/200 por rol | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py::test_sensores_user_403 -q` |
| 4 | CSRF fail-closed | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py::test_csrf_sin_origin_403 -q` |
| 5 | Sin secretos ni DB versionada | `git check-ignore -v backend/data/teiba_auth.db`; `git diff` |
| 6 | Suite completa en verde | `cd backend && .venv\Scripts\python.exe -m pytest -q` |

## Pasos (backend)
1. bcrypt + settings de auth — `feat: añadir autenticación SQLite`
2. domain/auth, application/auth, puertos, infrastructure, api/auth, deps — `feat: implementar login y sesiones`
3. Proteger endpoints, CSRF, rate limit, health — `feat: proteger API con RBAC y CSRF`
4. seed, .env, .gitignore, scripts — `chore: semilla de cuentas demo`
5. Tests + auditoría — `test: cubrir auth, sesión y permisos`

## Rollback
Revertir los commits de la rama; borrar `backend/data/teiba_auth.db` (gitignored);
restaurar el switch demo solo si se necesita volver atrás. No hay migración de datos
de dominio.

## Cierre
- Fila en `Docs/features/INDEX.md`; el switch demo de 003 queda superado.
- ADR 003; no hay cambio de esquema Mongo.
- El frontend se acoplará en una rama posterior (`feat/auth-ui-integración`),
  consumiendo los endpoints de este contrato.
