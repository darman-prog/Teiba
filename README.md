# Teiba — Panel Sage

Demo local del agente **Sage** para el monitoreo de parques urbanos de Teiba.
Sage responde en lenguaje natural usando herramientas de solo lectura sobre
MongoDB (`teiba_db`) y muestra las trazas de recuperación en un panel React.

## Stack

- Backend: Python 3.11+, FastAPI, PyMongo, SDK de OpenAI contra OpenCode Go.
- Frontend: React + TypeScript + Vite + Tailwind (pendiente de la fase 8).
- Datos: MongoDB 8 en Docker, base `teiba_db`.

## Requisitos

- Python 3.11 o superior.
- Node 20 o superior.
- Docker Desktop con la imagen `mongo:8`.
- Una `OPENCODE_API_KEY` válida.

## Arranque rápido

### 1. MongoDB y datos de la entrega

```powershell
docker run -d --name mongo-iot -p 27017:27017 -v mongo-iot-data:/data/db mongo:8
docker cp Scripts\01_crear_objetos.js mongo-iot:/tmp/01.js
docker cp Scripts\02_cargar_datos.js mongo-iot:/tmp/02.js
docker exec mongo-iot mongosh --quiet --file /tmp/01.js
docker exec mongo-iot mongosh --quiet --file /tmp/02.js
```

Los scripts `01` y `02` son los de la entrega; `02` borra y recarga las lecturas
originales con fecha fija. Después del seed de demo, no vuelvas a ejecutar `02`
sin volver a sembrar.

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
copy .env.example .env
# Edita backend\.env y define OPENCODE_API_KEY
.\.venv\Scripts\python.exe -m app.scripts.seed_demo
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`seed_demo` inserta lecturas frescas durante 12 h y deja tres casos para la demo:
SS-01 con pH 5.4, SS-02 sin reportar desde hace 7 h y SS-03 con batería 15 %.

### 3. Comprobaciones

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.scripts.check_health
.\.venv\Scripts\python.exe -m app.scripts.check_model
.\.venv\Scripts\python.exe -m app.scripts.smoke_demo
```

### 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

El panel abre en `http://localhost:5173` y consume `http://127.0.0.1:8000`
(la URL se configura con `VITE_API_URL`).

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
```

## Seguridad

- La API key vive solo en `backend/.env`; nunca en el frontend.
- El servidor escucha en `127.0.0.1`; el CORS acepta solo el puerto 5173.
- El endpoint del agente tiene rate limit y el LLM solo usa tools de lectura.

## Documentación

- Spec: `Docs/features/002-agente-sage-panel.md`.
- Decisión de arquitectura: `Docs/adr/002-stack-fastapi-react.md`.
- Modelo de datos canónico: `Docs/Diseno/ModeloDatos.md`.
- Guía de Postman y colección de ejemplos: `Docs/API/README.md`.
