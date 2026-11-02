# ADR 003: Autenticación local con SQLite y sesión por cookie

## Contexto

ADR 002 decidió "sin autenticación; solo `127.0.0.1`, CORS y rate limit". El usuario
pide un login real con tres roles de acceso (admin, operador y ciudadano). La colección Mongo
`usuarios` modela perfiles de dominio (administrador, operador, ciudadano) pero no
guarda contraseñas y no debe mezclarse con la capa de acceso.

## Decisión

- **SQLite solo para identidad y sesiones** (`users`, `sessions`). MongoDB sigue
  siendo la base de parques, sectores, dispositivos y lecturas.
- **Roles de acceso**: `admin`, `operator`, `user`; el rol de dominio
  (`administrador`, `operador_mantenimiento`, `ciudadano`) se lee de Mongo.
- **Token opaco** `secrets.token_urlsafe(32)`; en SQLite solo se guarda `sha256(token)`.
- **Cookie `teiba_session`**: `HttpOnly`, `SameSite=Lax`, `Path=/api`, `Max-Age=28800`
  (8 h absolutas, sin sliding), `Secure` configurable.
- **Contraseñas con bcrypt** (coste 12 prod / 4 tests). Seed idempotente de
  `admin@teiba.local`, `operador@teiba.local` y `user@teiba.local` desde
  `backend/.env`; sin passwords por defecto ni en el repo. Validación del límite de 72 bytes de bcrypt.
- **Perfil de dominio**: `login` y `/me` devuelven `perfil` leído de `usuarios` por
  correo normalizado; solo `id`, `nombre`, `correo` y `rol`. Si no existe o Mongo
  falla, `perfil: null` y la sesión sigue válida.
- **RBAC server-side**: `/api/parques` requiere sesión (admin, operator o user);
  `/api/sensores` y `/api/agente/consulta` solo admin (user/operator → 403);
  `/api/health` público.
- **CSRF fail-closed**: `Origin` obligatorio y en allowlist para todo POST/PUT/PATCH/DELETE.
- **Rate limit de login**: fallos por `(IP, correo)` con `Retry-After`.
- **Proxy Vite same-origin** (`/api -> 127.0.0.1:8000`), `apiBase()` vacío,
  `credentials:'include'`. CORS se mantiene exacto y sin credenciales.
- Un worker SQLite para la demo; WAL + `busy_timeout`; `.db` gitignored.

## Consecuencias

- Hay un segundo almacén; Mongo `usuarios` solo se lee para el perfil de dominio.
  El seed de mantenimientos crea los perfiles demo; hasta entonces `perfil: null`.
- La API deja de ser pública; el frontend debe consumir `/api/auth/login`.
- La demo no soporta multi-worker ni LAN; mantiene bind `127.0.0.1`.
- Logout y expiración revocan de verdad; no hay JWT ni refresh.

## Alternativas descartadas

- **JWT en localStorage**: XSS y sin revocación inmediata.
- **Contraseñas en Mongo**: mezcla auth con el modelo académico y no hay hashes.
- **CORS con credenciales**: más frágil que el proxy same-origin.
- **scrypt stdlib**: válido, pero las skills `seguridad`/`proteccion-datos` exigen
  bcrypt o argon2id.

## Sustituye parcialmente

- ADR 002 en lo referente a "sin autenticación". El resto (FastAPI, React, Mongo,
  CORS exacto, rate limit del agente) sigue vigente.
- Feature 003 (switch demo) queda superado por el login real (feature 007).
