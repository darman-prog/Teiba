# Teiba — Panel Sage y estación de campo

Demo local del agente **Sage** para parques urbanos: consulta sensores en lenguaje
natural, muestra las trazas de recuperación y suma libro de parques, mantenimientos
e incidentes con tres roles de acceso.

## Stack

- Backend: Python 3.11+, FastAPI, PyMongo, SQLite (identidad/sesión) y SDK de OpenAI
  contra OpenCode Go.
- Frontend: React 19 + TypeScript + Vite, Tailwind 4, React Router.
- Datos: MongoDB 8 en Docker, base `teiba_db`; SQLite local para usuarios y sesiones.

## Requisitos

- Python 3.11 o superior.
- Node 20 o superior.
- Docker Desktop con la imagen `mongo:8`.
- Una `OPENCODE_API_KEY` válida para el agente.

## Arranque rápido

### 1. MongoDB y datos de la entrega

```powershell
docker run -d --name mongo-iot -p 27017:27017 -v mongo-iot-data:/data/db mongo:8
docker cp Docs\Scripts\01_crear_objetos.js mongo-iot:/tmp/01.js
docker cp Docs\Scripts\02_cargar_datos.js mongo-iot:/tmp/02.js
docker exec mongo-iot mongosh --quiet --file /tmp/01.js
docker exec mongo-iot mongosh --quiet --file /tmp/02.js
```

> Los scripts viven en `Docs/Scripts/` y no se versionan por la regla `/Scripts`
> de `Docs/.gitignore`. Si clonas el repo, pídelos al equipo.

`02_cargar_datos.js` borra y recarga las lecturas con fecha fija. Después del
`seed_demo`, no lo vuelvas a ejecutar sin volver a sembrar.

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
copy .env.example .env
```

Edita `backend\.env` y define:

- `OPENCODE_API_KEY`: clave del agente (solo backend).
- `AUTH_ADMIN_PASSWORD`, `AUTH_OPERATOR_PASSWORD`, `AUTH_USER_PASSWORD`: contraseñas
  locales de las cuentas demo. Mínimo 12 caracteres; `seed_auth` aborta si faltan.

Después siembra en este orden y arranca:

```powershell
.\.venv\Scripts\python.exe -m app.scripts.seed_demo
.\.venv\Scripts\python.exe -m app.scripts.seed_auth
.\.venv\Scripts\python.exe -m app.scripts.seed_mantenimientos
.\.venv\Scripts\python.exe -m app.scripts.ensure_indexes
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- `seed_demo` inserta lecturas frescas durante 12 h (SS-01 con pH 5.4, SS-02 sin
  reportar y SS-03 con batería 15 %).
- `seed_auth` crea/actualiza las cuentas de acceso en SQLite (idempotente).
- `seed_mantenimientos` crea los perfiles de dominio en Mongo, más incidentes,
  elementos y tareas demo. Es idempotente.
- `ensure_indexes` deja el índice único de `usuarios.correo` y los índices de
  mantenimientos; ejecútalo tras el seed.
- El registro público (`/registro`) crea un ciudadano nuevo sin tocar el seed.

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Vite hace proxy de `/api` a `http://127.0.0.1:8000`,
así que la cookie de sesión viaja same-origin. Mantén ese proxy: la cookie es
`SameSite=Lax` y CORS no acepta credenciales cruzadas, así que un frontend en otro
origen no conservaría la sesión. `VITE_API_URL` solo cambia la base de las requests.

### 4. Comprobaciones

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.scripts.check_health
.\.venv\Scripts\python.exe -m app.scripts.check_model
.\.venv\Scripts\python.exe -m app.scripts.smoke_demo
```

## Roles y cuentas demo

| Acceso (`SQLite`) | Perfil (`Mongo`) | Correo demo | Home |
|---|---|---|---|
| `admin` | `administrador` | `admin@teiba.local` | `/sage` |
| `operator` | `operador_mantenimiento` | `operador@teiba.local` | `/mantenimientos` |
| `user` | `ciudadano` | `user@teiba.local` | `/parques` |

- Las contraseñas son las que definas en `backend/.env` (`AUTH_ADMIN_PASSWORD`,
  `AUTH_OPERATOR_PASSWORD`, `AUTH_USER_PASSWORD`); mínimo 12 caracteres, nunca se
  versionan ni se imprimen. Si cambias una, vuelve a ejecutar `seed_auth`.
- `otro@teiba.local` existe solo como perfil de Mongo para asignarle tareas; no tiene
  cuenta de acceso.
- Si un usuario queda sin perfil, `/perfil-no-configurado` lo explica y recuerda
  ejecutar `seed_mantenimientos`.

## Flujo de demo (2 minutos)

1. Entra como `admin@teiba.local` → estación Sage → pregunta
   “¿Cómo está el sensor de calidad del suelo del Sector Norte?”.
2. Cierra sesión y entra como `operador@teiba.local` → “Mis tareas” → abre una tarea
   asignada y finalízala con nota.
3. Cierra sesión y entra como `user@teiba.local` (o crea una cuenta en `/registro`)
   → libro de parques → abre una ficha.
4. Vuelve como admin → “Mantenimientos” para asignar, reasignar, finalizar o reabrir
   tareas y ver el incidente asociado.

## Consultas de la demo

1. “¿Cómo está el sensor de calidad del suelo del Sector Norte?”
   Debe responder por SS-01 y mostrar `list_sensors`, `get_sensor_history` y
   `get_device_context`.
2. “¿Qué sensores dependen de la antena ANT-01 y alguno está sin reportar?”
   Debe mostrar `get_devices_by_antenna` e identificar SS-02/MET-01.

## Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q -m integration
.\.venv\Scripts\python.exe -m ruff check .

cd ..\frontend
npm run typecheck
npm run lint
npm run test -- --run
npm run build
npm run check:ui
npm run detect:ui
```

## Seguridad

- La API key vive solo en `backend/.env`; nunca en el frontend ni en Git.
- La sesión usa la cookie `teiba_session` `HttpOnly`; no hay token en `localStorage`.
- Todo POST exige `Origin` permitido (CSRF fail-closed) y el login/registro tienen
  rate limit.
- El backend decide el rol; el registro público siempre crea `user`/ciudadano.
- El servidor escucha en `127.0.0.1` y CORS acepta solo el puerto 5173.

## Documentación

- Contexto completo del proyecto: [Docs/CONTEXT.md](Docs/CONTEXT.md).
- Registro de features: [Docs/features/INDEX.md](Docs/features/INDEX.md).
- Contrato y ejemplos de la API: [Docs/API/README.md](Docs/API/README.md).
- Decisión de arquitectura: [Docs/adr/002-stack-fastapi-react.md](Docs/adr/002-stack-fastapi-react.md).
- Decisión de auth: [Docs/adr/003-auth-sqlite.md](Docs/adr/003-auth-sqlite.md).
- Modelo de datos canónico: [Docs/Diseno/ModeloDatos.md](Docs/Diseno/ModeloDatos.md).
