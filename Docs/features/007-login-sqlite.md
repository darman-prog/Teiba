---
id: 007
status: cerrada
area: backend
tarea: -
created: 2026-10-31
updated: 2026-11-09
---
# Feature 007 — Login local con SQLite, roles y perfil de dominio

> Backend y frontend básico en `feat/auth-sqlite-backend`; el acabado visual queda para la rama UI.

## Objetivo
Permitir login real con tres roles de acceso (`admin`, `operator`, `user`), sesión
por cookie, RBAC server-side y `perfil` de dominio leído de Mongo `usuarios`.

## Alcance
| Incluye | Excluye |
|---|---|
| SQLite users/sessions v2, bcrypt, login/logout/me, cookie, RBAC, CSRF, rate limit, rol `operator`, perfil de dominio, AuthProvider/LoginView/guards/AccountMenu, tests y ADR | Registro, reset, 2FA, OAuth, JWT, multi-worker, estilos visuales nuevos |

## Criterios de aceptación
| N.º | Criterio verificable | Comando |
|---|---|---|
| 1 | Migración v1→v2 preserva usuarios/sesiones y admite operator | `cd backend && .venv\Scripts\python.exe -m pytest tests/integration/test_sqlite_auth_repository.py -q` |
| 2 | Login/cookie/401/429/logout/me | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py -q` |
| 3 | RBAC 401/403/200 por rol | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_parks_api.py -q` |
| 4 | CSRF fail-closed | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py::test_csrf_sin_origin_403 -q` |
| 5 | Perfil de dominio, null y sin PII | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py -q` |
| 6 | Sin secretos ni DB versionada | `git check-ignore -v backend/data/teiba_auth.db`; `git diff` |
| 7 | Suite completa en verde | `cd backend && .venv\Scripts\python.exe -m pytest -q` |
| 8 | Lint limpio | `cd backend && .venv\Scripts\python.exe -m ruff check .` |
| 9 | Frontend compila, prueba y axe | `cd frontend && npm run typecheck && npm run lint && npm run test -- --run && npm run build` |

## Pasos
1. Rol operator + migración SQLite v2 — `feat: añadir rol operador y perfil de dominio al login`
2. Perfil de dominio + tests backend — incluido en el paso 1
3. Login, guards y AccountMenu — `feat: montar login y guards en el frontend`
4. Tests frontend y axe — incluido en el paso 3

## Rollback
Revertir los commits de la rama; borrar `backend/data/teiba_auth.db` (gitignored);
restaurar el switch demo solo si se necesita volver atrás. No hay migración de datos
de dominio.

## Cierre
- Fila en `Docs/features/INDEX.md`; el switch demo de 003 queda superado.
- ADR 003; no hay cambio de esquema Mongo.
- El frontend básico usa `{usuario, perfil, expira_en}` y cookie httpOnly; el
  acabado visual lo hará la rama de UI.
