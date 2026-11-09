---
id: 012
status: cerrada
area: frontend
tarea: -
created: 2026-11-09
updated: 2026-11-09
---
# Feature 012 — Registro público y acceso visual MVP

> Cierra el acceso para demostrar los tres roles: login existente, alta de ciudadano
> en `/registro` y README de montaje. El agente Sage queda en la sesión paralela.

## Objetivo
Que un visitante cree su cuenta de ciudadano y que las tres cuentas demo se puedan
mostrar con un montaje reproducible en local.

## Contexto
007 dejó login, cookie HttpOnly, RBAC y perfil de dominio. Faltaba el alta pública,
el enlace visual y un README al día: el documento aún describía el template de Vite.
El frontend ya tenía `LoginView`, `AuthProvider`, guards y `AccountMenu`.

## Alcance
| Incluye | Excluye |
|---|---|
| `RegisterRequest`, `create_usuario`/`create_perfil`, `AuthService.register` con compensación SQLite↔Mongo, `POST /api/auth/register`, rate limit por IP, `RegisterView`, `AuthLayout`/`AuthField`, ruta `/registro`, README, API docs y tests | Alta de operadores desde UI, reset, 2FA, OAuth, captcha, cambios en el agente, migración de esquema |

## Criterios de aceptación
| N.º | Criterio verificable | Comando | Evidencia |
|---|---|---|---|
| 1 | Registro público crea `user` + perfil `ciudadano`, cookie y rechaza `rol` del cliente | `cd backend && .\.venv\Scripts\python.exe -m pytest tests/api/test_auth_register_api.py -q` | 10 passed |
| 2 | Login/CSRF/RBAC existentes no se rompen | `cd backend && .\.venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py -q` | 22 passed |
| 3 | Suite backend y lint | `cd backend && .\.venv\Scripts\python.exe -m pytest -q && .\.venv\Scripts\python.exe -m ruff check .` | 156 passed, 22 skipped; ruff 0 |
| 4 | Registro y rutas de auth en frontend | `cd frontend && npx vitest run src/features/auth src/app/AuthRoutes.test.tsx src/app/App.axe.test.tsx` | 26 passed |
| 5 | Frontend compila, prueba y build | `cd frontend && npm run typecheck && npm run lint && npx vitest run && npm run build` | 57 passed |
| 6 | Accesibilidad y tokens | `cd frontend && npm run check:ui && npm run detect:ui` | OK / `[]` |
| 7 | README sin secretos ni claves | `Select-String README.md,Docs/API/README.md -Pattern 'AUTH_\w+PASSWORD=\S+|admin12345678|operator12345678|user12345678'` | 0 matches |

## Pasos
1. Contrato, puertos, repos SQLite/Mongo, servicio con compensación y endpoint — `feat: registrar cuentas de ciudadano con sqlite y mongo`
2. Cliente, provider, ruta `/registro`, `AuthLayout` y `RegisterView` + tests — `feat: conectar registro y pulir el acceso del mvp`
3. README, API, CONTEXT y esta spec — `docs: documentar montaje y roles demo`

## Bitácora
| Criterio | Fecha | Comando | Exit | Commit |
|---|---|---|---|---|
| 1 | 2026-11-09 | cd backend && .\.venv\Scripts\python.exe -m pytest tests/api/test_auth_register_api.py -q | 0 | 7536fd4 |
| 2 | 2026-11-09 | cd backend && .\.venv\Scripts\python.exe -m pytest tests/api/test_auth_api.py -q | 0 | 7536fd4 |
| 3 | 2026-11-09 | cd backend && .\.venv\Scripts\python.exe -m pytest -q && .\.venv\Scripts\python.exe -m ruff check . | 0 | 7536fd4 |
| 4 | 2026-11-09 | cd frontend && npx vitest run src/features/auth src/app/AuthRoutes.test.tsx src/app/App.axe.test.tsx | 0 | 3ce92ce |
| 5 | 2026-11-09 | cd frontend && npm run typecheck && npm run lint && npx vitest run && npm run build | 0 | 3ce92ce |
| 6 | 2026-11-09 | cd frontend && npm run check:ui && npm run detect:ui | 0 | 3ce92ce |
| 7 | 2026-11-09 | Select-String README.md,Docs/API/README.md -Pattern 'AUTH_\w+PASSWORD=\S+|admin12345678|operator12345678|user12345678' | 0 | a15fc85 |

## Rollback
Revertir los commits de `feat/auth-register-mvp`; no hay migración de datos. Los
usuarios creados por el registro quedan en SQLite/Mongo y se pueden borrar a mano.
El seed de auth restaura las cuentas demo.

## Cierre
- Fila resumen en `Docs/features/INDEX.md`.
- Decisión de arquitectura: no aplica; el alta es aditiva y reversible. La
  compensación SQLite→Mongo queda documentada porque Mongo standalone no ofrece
  transacciones multi-documento.
