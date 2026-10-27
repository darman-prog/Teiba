# Teiba — Contexto completo del proyecto

> Documento único de entrada para personas y agentes. Resume el producto, la
> arquitectura, el modelo de datos, el backend, el contrato de API, el brief de
> diseño y el estado actual.
>
> Última actualización: 2026-10-24 · Estado técnico verificado: `2239f47` ·
> Backend y seed listos; frontend pausado para prototipos de diseño.
>
> El detalle canónico vive en los archivos enlazados en la sección 13. Este
> documento no duplica el schema completo, el ADR completo ni la spec completa.

## Mapa de lectura

| Si buscas… | Lee |
|---|---|
| Producto, alcance y decisiones | Secciones 1–3 |
| Arquitectura y RAG | Sección 4 |
| Modelo de datos y seed | Sección 5 |
| Backend, tools y agente | Sección 6 |
| Contrato HTTP | Sección 7 |
| Estado del frontend | Sección 8 |
| Brief para prototipos | Sección 9 |
| Cómo levantar todo | Sección 10 |
| Estado, tests y pendientes | Secciones 11 y 16 |
| Reglas del repositorio | Sección 12 |
| Erratas y decisiones descartadas | Sección 14 |
| Glosario | Sección 15 |

## 0. Ficha rápida

| Campo | Valor |
|---|---|
| Proyecto | **Teiba** — “hilos de datos, parques vivos” |
| Curso | Bases de Datos II, Ingeniería de Sistemas, UNAB |
| Agente | **Sage** |
| Stack | FastAPI + MongoDB 8 + React/Vite/TypeScript; Tailwind pendiente |
| Base de datos | `teiba_db` |
| Repositorio | `https://github.com/darman-prog/Teiba.git` |
| Rama | `main` |
| Estado | Backend y seed listos; frontend en pausa por prototipos |
| Verificación | 76 tests, `ruff` limpio, criterios 1/2/5/7 registrados |
| Última actualización | 2026-10-24 |

## 1. Qué es Teiba

Teiba es una plataforma académica para gestionar parques urbanos del área
metropolitana de Bucaramanga y monitorear sus dispositivos IoT. El sistema cubre
parques, sectores, dispositivos, telemetría, inventario, mantenimientos,
incidentes ciudadanos y usuarios.

El componente diferencial es **Sage**, un agente que responde en lenguaje natural
sobre el estado de los sensores. Sage no consulta Mongo directamente ni inventa
datos: usa herramientas de solo lectura, recibe resultados acotados y redacta una
respuesta trazable.

### Las 8 entidades del modelo

| Colección | Propósito |
|---|---|
| `parques` | Espacios públicos, ubicación GeoJSON, área, tipo y estado |
| `sectores` | Zonas internas de cada parque, tipo de suelo y riesgo |
| `dispositivos` | Sensores, antenas, luminarias y estaciones meteorológicas |
| `lecturas` | Serie temporal de telemetría ambiental |
| `elementos_inventario` | Mobiliario urbano e infraestructura física |
| `mantenimientos` | Órdenes preventivas y correctivas |
| `incidentes` | Reportes ciudadanos con prioridad y estado |
| `usuarios` | Administradores, operadores y ciudadanos |

### Valor de la demo

- **Interfaz natural:** el operador pregunta sin conocer IDs ni colecciones.
- **Orquestación:** Sage decide qué tools llamar y en qué orden.
- **Interpretación:** la tool evalúa rangos; el LLM solo narra.
- **Trazabilidad:** el panel muestra tools, argumentos y tiempos.
- **Cruce de datos:** une telemetría, dispositivo, sector y parque.

### Lo que Teiba no es

- No es un sistema en producción ni tiene tráfico real.
- No usa Neo4j, base de grafos, embeddings ni búsqueda vectorial.
- No tiene autenticación ni está pensado para exponerse a Internet.
- No incluye CRUD de parques, mapas, gráficas históricas ni actuadores físicos.

## 2. Alcance, no objetivos y decisiones

### Incluye

- Modelo documental MongoDB de 8 colecciones y scripts de la entrega.
- Backend FastAPI con health, catálogo de sensores y consulta al agente.
- Cuatro tools de solo lectura, validación estricta y evaluación de rangos.
- Panel React de una sola página: chat, trazas y tira de sensores.
- Seed de demo con lecturas frescas y anomalías controladas.
- Tests unitarios, de integración y de contrato HTTP.
- Documentación de arquitectura, spec, API y contexto.

### Excluye

- Neo4j, base de grafos, embeddings y RAG vectorial.
- Autenticación, autorización, multiusuario y despliegue público.
- CRUD de parques, sectores, inventario, mantenimientos o incidentes.
- Mapas, gráficas, reportes descargables y acciones físicas.
- Edición del documento Word de la entrega.
- Uso de las otras cuatro colecciones en el panel.

### Decisiones vigentes

| Decisión | Motivo |
|---|---|
| MongoDB como motor único | Simplicidad académica y una sola fuente de datos |
| RAG por herramientas | Recuperación determinista y verificable, sin vectores |
| FastAPI | Backend pequeño, tipado y con OpenAPI gratis |
| React + Vite + TypeScript | Componentes modernos sin la ceremonia de Angular |
| Tailwind | Tokens y utilidades para una UI propia |
| DeepSeek como modelo principal | Costo y disponibilidad; LongCat 2.0 como respaldo |
| Sin autenticación | Demo local en `127.0.0.1`; no se expone a LAN |
| `teiba_db` | Nombre usado por los scripts y el ADR 001 |

## 3. Usuarios y flujos de la demo

| Usuario | Necesidad |
|---|---|
| Administrador u operador de parques | Saber el estado de un sensor sin conocer IDs ni colecciones |
| Profesor evaluador | Ver que el agente consulta datos reales y que las tools son auditables |
| Desarrollador | Reproducir la demo y entender dónde vive cada responsabilidad |

### Flujo 1 — Consulta principal

1. El operador escribe: “¿Cómo está el sensor de calidad del suelo del Sector Norte?”
2. Sage llama `list_sensors(tipo="calidad_suelo", sector="Sector Norte")`.
3. Sage llama `get_sensor_history(sensor_id="SS-01", horas=6)`.
4. Sage llama `get_device_context(device_id="SS-01")`.
5. Responde con SS-01, Sector Norte, humedad 38.0 %, pH 5.4, temperatura 19.0 °C
   y explica que el pH está bajo el rango normal.
6. El panel muestra las tres trazas con argumentos y duración.

### Flujo 2 — Orquestación con antena

1. El operador pregunta: “¿Qué sensores dependen de la antena ANT-01 y alguno
   está sin reportar?”
2. Sage llama `get_devices_by_antenna(antena="ANT-01")`.
3. La tool devuelve SS-01, SS-02 y MET-01; SS-02 lleva 7 h sin reportar y MET-01
   no tiene lecturas.
4. Sage sintetiza la respuesta y el panel muestra la traza.

### Lo que debe verse en pantalla

- Una conversación clara, no un volcado de JSON.
- Las tools invocadas, con nombre, argumentos y estado.
- El estado de los sensores de un vistazo.
- La diferencia entre dato actual, dato antiguo y dato inexistente.

## 4. Arquitectura

### Vista física

```text
┌─────────────────────────┐
│ Navegador               │
│ React SPA (Vite)        │  HTTP/JSON
│ componentes + hooks     │ ─────────────┐
└─────────────────────────┘              │
                                         ▼
                              ┌──────────────────────────┐
                              │ FastAPI (1 proceso)      │
                              │ API → aplicación → dominio│
                              │        ↑                 │
                              │   infraestructura        │
                              └───────┬──────────┬───────┘
                                      │          │
                                      ▼          ▼
                                ┌──────────┐  ┌──────────────┐
                                │ MongoDB  │  │ OpenCode Go  │
                                │ teiba_db │  │ (LLM externo)│
                                └──────────┘  └──────────────┘
```

Cuatro nodos en runtime: navegador, FastAPI, MongoDB y OpenCode Go. El navegador
no habla con Mongo ni con el LLM; FastAPI es el único con credenciales.

### Cliente-servidor y monolito modular

- El cliente es una **SPA** de un solo artefacto, organizada por componentes.
- El servidor es un **monolito modular por capas** con puertos/adaptadores.
- No hay microservicios: un proceso FastAPI, una base y un LLM externo.
- El contrato HTTP es la única unión entre cliente y servidor.

### Capas del backend

| Capa | Responsabilidad | Depende de |
|---|---|---|
| `api/` | Routers, DTOs, validación, errores, `traceId`, rate limit | aplicación |
| `application/` | Casos de uso, bucle del agente, tools, puertos | dominio |
| `domain/` | Rangos, evaluación, errores e invariantes | nada |
| `infrastructure/` | Repositorios PyMongo, cliente LLM, reloj | implementa puertos |

Regla: `api → application → domain`; `infrastructure` implementa interfaces y se
inyecta en `main.py`. Puertos: `DeviceRepository`, `ReadingRepository`,
`LLMClient`, `Clock`.

### Capas del frontend

| Capa | Responsabilidad | Regla |
|---|---|---|
| `components/` | UI presentacional | Sin `fetch`, sin reglas de negocio |
| `hooks/` | `useAgent`, `useSensors` | Orquestan el cliente API |
| `api/` | Cliente HTTP y parseo de errores | Único lugar con `fetch` |
| `types/` | DTOs espejo del contrato | `snake_case` |
| `lib/` | Formato de fechas, números y estados | Funciones puras |

El frontend no duplica la evaluación de rangos: esa regla vive en el backend.

### RAG por herramientas

El RAG **no es un nodo separado**. Es el circuito que va de MongoDB a FastAPI,
de FastAPI al LLM y de vuelta a FastAPI. La recuperación vive en las tools y
repositorios; la aumentación, en el bucle; la generación, en OpenCode Go.

```text
┌──────────────────────────── FastAPI ────────────────────────────┐
│  api/          routers, DTOs, errores, traceId                   │
│                                                                 │
│  ┌──────────── RAG por herramientas (patrón) ────────────────┐  │
│  │ application/agent/loop.py                                  │  │
│  │   1. pregunta + schemas de tools → LLM                     │  │
│  │   2. tool_call                                             │  │
│  │   3. tool contra MongoDB                        ← R        │  │
│  │   4. resultado inyectado en el contexto         ← A        │  │
│  │   5. respuesta final                            ← G        │  │
│  └────────────────────────────────────────────────────────────┘  │
│           │                                      │              │
│  domain/  │ rangos y evaluación                 │              │
│  infra/   │ repositorios PyMongo                 │ cliente LLM  │
└───────────┼──────────────────────────────────────┼──────────────┘
            ▼                                      ▼
      ┌──────────┐                          ┌──────────────┐
      │ MongoDB  │                          │ OpenCode Go  │
      │ teiba_db │                          │ (generador)  │
      └──────────┘                          └──────────────┘
```

| Fase | Dónde vive | Qué hace |
|---|---|---|
| **R** | `application/tools` + `infrastructure/repositories` | Consultas deterministas a `lecturas`, `dispositivos`, `sectores`, `parques` |
| **A** | `application/agent/loop.py` | Arma mensajes, ejecuta tools y añade resultados al contexto |
| **G** | `infrastructure/llm` + OpenCode Go | Redacta usando solo lo recuperado |

Secuencia resumida:

```text
Operador -> React: pregunta
React -> FastAPI: POST /api/agente/consulta
FastAPI -> LLM: system prompt + pregunta + schemas
LLM -> FastAPI: tool_call
FastAPI -> MongoDB: consulta de la tool
MongoDB -> FastAPI: resultado acotado
FastAPI -> LLM: resultado como mensaje de tool
LLM -> FastAPI: respuesta final
FastAPI -> React: respuesta + trazas
```

El detalle completo, con diagramas y defensa, está en el
[ADR 002](Docs/adr/002-stack-fastapi-react.md).

### Despliegue local

- Desarrollo: Vite en `:5173`, FastAPI en `:8000`, MongoDB en `:27017`.
- El backend escucha en `127.0.0.1`; no se expone a la LAN.
- Para la demo se puede servir el build de React desde FastAPI, pero no es
  obligatorio.
- El LLM es un servicio externo: sin red o sin key, el agente no responde.

## 5. Modelo de datos

La fuente canónica es [ModeloDatos.md](Docs/Diseno/ModeloDatos.md) §3.1/§3.3.
Este resumen no reemplaza ese documento.

### Base y colecciones

- Base: `teiba_db`.
- 8 colecciones: `parques`, `sectores`, `dispositivos`, `lecturas`,
  `elementos_inventario`, `mantenimientos`, `incidentes`, `usuarios`.
- La app usa solo las cuatro primeras. Las otras cuatro quedan intactas.

### Colecciones que usa el panel

| Colección | Campos relevantes | Tipos |
|---|---|---|
| `parques` | `_id`, `codigo`, `nombre`, `ubicacion{direccion,comuna,coordenadas}`, `area_m2`, `tipo_parque`, `estado_general` | ObjectId, String, GeoJSON Point, Double |
| `sectores` | `_id`, `codigo`, `parque_id`, `nombre`, `tipo_suelo`, `zona_riesgo` | ObjectId, String |
| `dispositivos` | `_id`, `tipo`, `marca`, `fecha_instalacion`, `sector_id`, `parque_id`, `depende_de`, `alimentado_por` | String, Date, ObjectId, String/null |
| `lecturas` | `timestamp`, `meta.sensor_id`, `meta.tipo`, `humedad`, `ph`, `temperatura`, `bateria` | Date, String, Double, Int32 |

### `lecturas` es time-series y plana

```javascript
db.createCollection("lecturas", {
  timeseries: {
    timeField: "timestamp",
    metaField: "meta",
    granularity: "minutes"
  }
});
db.lecturas.createIndex({ "meta.sensor_id": 1, "timestamp": -1 });
```

La telemetría va en la raíz del documento; no hay un subdocumento anidado de
métricas. `meta` solo agrupa `sensor_id` y `tipo`.

### Invariante de integridad

Para cada dispositivo:

```text
dispositivos.parque_id == sectores[dispositivos.sector_id].parque_id
```

Un dispositivo no puede apuntar a un sector de otro parque.

### Ejemplo canónico

- Sensor: **SS-01**.
- Sector: **SEC-001**, “Sector Norte - Jardines de la Escultura de Botero”.
- Parque: **Parque San Pío**.
- Antena: **ANT-01**.
- Energía: `Panel_Solar_PS1`.

### Seed de demo

El seed vive en `backend/app/scripts/seed_demo.py` y es idempotente:

- Borra solo `{"meta.origen": "demo"}` y vuelve a insertar.
- Inserta 217 lecturas: 49 por sensor de suelo, cada 15 min, últimas 12 h.
- SS-01 tiene pH 5.4 en la última lectura.
- SS-02 tiene su última lectura hace 7 h (21 lecturas, sin datos recientes).
- SS-03 tiene batería 15 % en las últimas cuatro lecturas.
- MET-01 no recibe lecturas.
- Las 15 lecturas originales de `02_cargar_datos.js` se conservan.

Anomalías deliberadas:

| Sensor | Estado | Motivo |
|---|---|---|
| SS-01 | danger | pH 5.4, fuera de 6.0–7.5 |
| SS-02 | warning | última lectura hace 7 h |
| SS-03 | danger | batería 15 %, menor que 20 % |
| SS-04 | ok | valores normales |
| SS-05 | ok | valores normales |
| MET-01 | sin datos | no tiene telemetría en el seed |

No ejecutes `02_cargar_datos.js` después del seed: borra las lecturas. Si lo
haces, vuelve a ejecutar `seed_demo`.

## 6. Backend y agente Sage

### Stack y versiones

| Componente | Versión usada |
|---|---|
| Python | 3.13.14 |
| FastAPI | 0.162.0 |
| Uvicorn | 0.54.0 |
| PyMongo | 4.19.0 |
| SDK de OpenAI | 3.37.0 |
| Pydantic Settings | 2.16.1 |
| MongoDB | 8 (contenedor `mongo-iot`) |

### Estructura

```text
backend/
├── app/
│   ├── main.py, config.py, db.py, schemas.py
│   ├── api/          agent, deps, errors, health, middleware, sensors
│   ├── application/  errors, ports, serializers
│   ├── domain/       ranges
│   ├── infrastructure/ clock, llm, mongo_repositories
│   ├── agent/        cache, loop, prompts, tools, validation
│   └── scripts/      seed_demo, check_health, check_model, smoke_demo
├── tests/            api, integration, unit
├── requirements.txt, requirements-dev.txt
├── pyproject.toml, pytest.ini, .env.example
```

### Tools

| Tool | Argumentos | Devuelve |
|---|---|---|
| `list_sensors` | `tipo?`, `sector?`, `parque?`, `depende_de?`, `limite` 1–50 | Dispositivos con sector, parque, comuna y antena |
| `get_sensor_history` | `sensor_id`, `horas` 1–168, `limite` 1–50 | Estado de datos, lecturas, última lectura, antigüedad y evaluación |
| `get_device_context` | `device_id` | Dispositivo, sector, parque, antena padre y dependientes |
| `get_devices_by_antenna` | `antena` | Hijos directos, última lectura, `sin_reportar` y motivo |

Reglas:

- Validación Pydantic con `extra="forbid"`.
- Se rechazan `$`, `.`, dicts y claves extra.
- Los IDs son alfanuméricos cortos; los nombres de sector/parque tienen límite.
- Una tool sin resultados devuelve un estado explícito, no vacío silencioso.
- El dispatcher es una allowlist y captura excepciones; nunca devuelve un 500 al
  modelo.

### Rangos operativos

| Métrica | Rango normal |
|---|---|
| pH | 6.0 – 7.5 |
| Humedad | 30 – 60 % |
| Temperatura | 15 – 28 °C |
| Batería | 20 – 100 % |

La evaluación la hace `domain/ranges.py`; el LLM recibe `evaluacion` ya calculada
y no debe hacer comparaciones por su cuenta.

### Bucle del agente

- `temperature=0`, `max_pasos=6`, `max_tokens=600`.
- Timeout de 30 s por llamada y 60 s total.
- Grounding estricto: toda afirmación debe salir de una tool.
- Si el modelo responde sin tools, se le obliga a intentarlo de nuevo; si
  insiste, se devuelve un fallback determinista.
- Se detectan llamadas repetidas con los mismos argumentos.
- Errores tipados: `invalid_args`, `not_found`, `not_a_sensor`, `sin_datos`,
  `db_error`.
- Reintento único en 429/5xx; 401/402 no se reintentan.
- Caché en memoria de 10 min para la última respuesta exitosa.
- Modelos permitidos: DeepSeek (principal) y LongCat 2.0 (respaldo). Kimi y GLM
  no se prueban por costo.

### Tests

- 76 tests pasan.
- Unitarios: rangos, validación, tools, bucle con LLM falso.
- Integración: repositorios contra `teiba_test` y contrato de esquema contra
  `teiba_db`.
- API: health, errores, CORS, rate limit, agente, sensores y seguridad.
- `ruff check .` limpio.

Comandos:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q -m integration
.\.venv\Scripts\python.exe -m ruff check .
```

## 7. Contrato de API

La API no está versionada en la URL porque es un contrato local único. Todos los
campos usan `snake_case`, salvo `traceId` en el contrato de errores.

| Método | Ruta | Entrada | Éxito |
|---|---|---|---|
| `GET` | `/api/health` | — | 200 con `status`, `mongo`, `llm`, `version` |
| `GET` | `/api/sensores` | `tipo`, `limite` | 200 con `items[]` y `total` |
| `POST` | `/api/agente/consulta` | `{ "pregunta": "..." }` | 200 con `respuesta`, `trazas[]`, `meta` |
| `GET` | `/docs` | — | Swagger UI |
| `GET` | `/openapi.json` | — | Contrato OpenAPI |

### Health

```json
{
  "status": "ok",
  "mongo": { "ok": true, "db": "teiba_db" },
  "llm": { "configurado": true, "modelo": "deepseek-v4.1-flash" },
  "version": "0.1.0"
}
```

Devuelve 200 incluso en estado `degraded`; hay que leer el body. No expone URI,
versión de Mongo ni la key.

### Sensores

```json
{
  "items": [
    {
      "id": "SS-01",
      "tipo": "calidad_suelo",
      "marca": "SoilPro-Sense LoRa",
      "sector": "Sector Norte - Jardines de la Escultura de Botero",
      "sector_id": "671151000000000000000001",
      "parque": "Parque San Pío",
      "comuna": "Comuna 12 - Cabecera del Llano",
      "depende_de": "ANT-01",
      "alimentado_por": "Panel_Solar_PS1",
      "ultima_lectura": {
        "timestamp": "2026-10-24T18:00:00Z",
        "humedad": 38.0,
        "ph": 5.4,
        "temperatura": 19.0,
        "bateria": 95,
        "antiguedad_min": 0
      },
      "estado": "danger"
    }
  ],
  "total": 1
}
```

- `estado`: `ok`, `warning`, `danger` o `sin_datos`.
- `danger` tiene prioridad sobre `warning`.
- `total` es la cantidad devuelta, no el total de la colección.
- `sector_id` es el ObjectId en string; el código legible `SEC-001` aparece en
  los resultados de las tools, no en este DTO.

### Consulta al agente

Request:

```json
{ "pregunta": "¿Cómo está el sensor de calidad del suelo del Sector Norte?" }
```

Response resumida:

```json
{
  "respuesta": "El sensor SS-01, en el Sector Norte del Parque San Pío, reporta humedad de 38.0 %, pH de 5.4 y temperatura de 19.0 °C. El pH está por debajo del rango normal (6.0–7.5).",
  "trazas": [
    {
      "tool": "list_sensors",
      "args": { "tipo": "calidad_suelo", "sector": "Sector Norte" },
      "ok": true,
      "ms": 8,
      "resumen": "1 dispositivo: SS-01",
      "resultado": "{\"estado\": \"ok\", ...}"
    }
  ],
  "meta": {
    "modelo": "deepseek-v4.1-flash",
    "pasos": 4,
    "duracion_ms": 4200,
    "cached": false,
    "trace_id": "..."
  }
}
```

- `trazas[].resultado` es un string JSON truncado, no un objeto.
- `meta.cached` es `true` si repites la misma pregunta dentro de 10 min.
- `meta.trace_id` sale del header `X-Request-Id` o se genera.
- La consulta puede tardar hasta 60 s.

### Errores

```json
{
  "code": "invalid_request",
  "message": "Los datos enviados no son válidos.",
  "details": [{ "loc": ["body", "pregunta"], "msg": "...", "type": "..." }],
  "traceId": "..."
}
```

| HTTP | `code` | Cuándo |
|---|---|---|
| 422 | `invalid_request` | Query o body inválido |
| 429 | `rate_limited` | Más de 10 consultas/min o 2 concurrentes |
| 502 | `llm_unavailable` | OpenCode Go no responde |
| 503 | `llm_not_configured` | Falta la key o es inválida |
| 503 | `db_unavailable` | MongoDB caído |
| 504 | `timeout` | La consulta superó el tiempo máximo |
| 404 | `not_found` | Ruta inexistente |
| 500 | `internal_error` | Error no controlado |

### Límites y seguridad

- Rate limit: 10 POST/min por IP, 2 concurrentes, ventana de 60 s.
- Pregunta: 3–500 caracteres.
- CORS: solo `http://localhost:5173` y `http://127.0.0.1:5173`.
- Bind: `127.0.0.1`; no exponer a LAN.
- Key solo en `backend/.env`; nunca en el frontend.
- `X-Trace-Id` en todas las respuestas.

La guía de Postman, con ejemplos y tests, está en
[Docs/API/README.md](Docs/API/README.md).

## 8. Frontend y estado actual

El frontend existe solo como **scaffold de Vite**:

- React 19.3.1, Vite 8.3.4, TypeScript 6.0.3, `@vitejs/plugin-react`.
- `oxlint` como linter.
- Sin Tailwind, sin `lucide-react`, sin tests y sin `node_modules`.
- `src/App.tsx` sigue siendo el template de Vite.

La UI está **pausada** hasta que existan los prototipos de diseño. Cuando se
retome, la estructura objetivo es:

```text
frontend/src/
├── components/   UI presentacional
├── hooks/        useAgent, useSensors
├── api/          client, agent, sensors
├── types/        DTOs del contrato
├── lib/          formato y utilidades
└── test/         setup de Vitest
```

Reglas:

- Los componentes no llaman `fetch` directamente.
- El cliente API centraliza timeout y parseo de errores.
- No se duplican rangos ni evaluación de dominio.
- La key y la URI de Mongo nunca llegan al navegador.
- Tailwind y los tokens se instalan al iniciar el paso 8.

## 9. Brief de diseño del panel

### Objetivo visual

Un panel de operaciones de parques, no un chatbot genérico. En cinco segundos
debe entenderse que hay un agente, una base de datos y trazas verificables.

### Dirección

“Claro orgánico”: fondo cálido, verdes profundos, acento dorado y tipografía
editorial. La metáfora es “hilos de datos, parques vivos”.

| Token | Valor |
|---|---|
| Fondo | `#F7F5EF` |
| Superficie | `#FFFFFF` |
| Tinta | `#1C2B24` |
| Texto secundario | `#5E6B63` |
| Primario | `#1F6F4A` |
| Primario suave | `#E6F0EA` |
| Acento | `#C9A227` |
| Borde | `#E4E0D6` |
| Warning | `#B54708` |
| Danger | `#B42318` |
| Success | `#027A48` |

Tipografía: **Fraunces** para títulos y marca; **Manrope** para UI y cuerpo;
monospace del sistema para argumentos y JSON.

Formas: radios 12–16 px, bordes de 1 px, sombras suaves, iconos lucide de 1.5 px.
Nada de gradientes morados, glassmorphism, robots, fotos de stock ni sparkles por
todas partes.

### Layout

1. Header fijo: “Teiba · Sage”, subtítulo, pills de Mongo/modelo/demo y acción
   “Nueva consulta”.
2. Tira de 5 sensores de suelo: ID, sector, última lectura, batería y estado.
3. Chat a la izquierda (8/12), trazas a la derecha (4/12).
4. Input fijo al fondo del chat con sugerencias en el estado vacío.
5. Móvil: una columna; tira con scroll horizontal; trazas en acordeón.

### Pantallas

P0:

1. Desktop 1440, estado inicial con 3 sugerencias.
2. Desktop 1440, respuesta de Sage con 3 trazas.
3. Móvil 390, misma conversación.

P1:

4. Carga: “Sage está consultando la base de datos…”.
5. Error con `traceId`, botón “Reintentar” y pregunta conservada.
6. Hoja de componentes y estados.

P2:

7. Traza expandida con JSON del resultado y scroll interno.

### Datos de ejemplo

| Sensor | Sector | Última lectura | Estado |
|---|---|---|---|
| SS-01 | Sector Norte - Jardines | pH 5.4; humedad 38.0 %; 19.0 °C; batería 95 % | danger por pH |
| SS-02 | Sector Sur - Plazoleta | hace 7 h; pH 6.5; humedad 40.0 %; 19.7 °C | warning por antigüedad |
| SS-03 | Sector Bosque | pH 6.6; humedad 42.0 %; 20.4 °C; batería 15 % | danger por batería |
| SS-04 | Sector Occidental | pH 6.5; humedad 44.0 %; 21.1 °C; batería 86 % | ok |
| SS-05 | Sendero de la Quebrada | pH 6.5; humedad 46.0 %; 21.8 °C; batería 83 % | ok |

Sugerencias del estado vacío:

1. “¿Cómo está el suelo del Sector Norte?”
2. “¿Qué sensores dependen de ANT-01?”
3. “¿Hay algún sensor con batería baja?”

Traza esperada de la consulta principal:

| Tool | Args | Resumen |
|---|---|---|
| `list_sensors` | `{"tipo":"calidad_suelo","sector":"Sector Norte"}` | 1 dispositivo: SS-01 |
| `get_sensor_history` | `{"sensor_id":"SS-01","horas":6}` | 49 lecturas; pH fuera de rango |
| `get_device_context` | `{"device_id":"SS-01"}` | Sector Norte / ANT-01 |

### Interacciones

- Clic en tarjeta de sensor: precarga “¿Cómo está el sensor SS-01?” y enfoca el
  input.
- Enviar: burbuja del usuario, carga, respuesta y trazas.
- Expandir/colapsar una traza.
- Reintentar conserva la pregunta.
- “Nueva consulta” vuelve al estado vacío.
- `Enter` envía; `Shift+Enter` salta línea.

### Accesibilidad

- Contraste AA: 4.5:1 en texto y 3:1 en UI.
- Estado con icono + texto, no solo color.
- Foco visible de 2 px.
- `aria-live="polite"` para la respuesta nueva.
- Labels reales, errores anunciados y `prefers-reduced-motion`.
- Objetivos táctiles de 24×24 px como mínimo; 44×44 en móvil.

### Entregables de diseño

- Frames 1440×1024 y 390×844.
- Hoja de componentes: botones, input, chips, tarjetas, badges, trazas, banners.
- Tokens de color, tipografía, espaciado, radios y sombras.
- Anotaciones de comportamiento, responsive y accesibilidad.
- Nombres: `01-panel-inicial`, `02-conversacion`, `03-movil`, `04-cargando`,
  `05-error`, `06-componentes`, `07-traza-expandida`.

Este apartado es el brief vigente para los prototipos; no hace falta el prompt
largo para empezar.

## 10. Operación y reproducción

### Requisitos

- Python 3.11+; el equipo usa 3.13.
- Node 20+; el equipo usa 24.
- Docker Desktop con `mongo:8`.
- `OPENCODE_API_KEY` válida para probar el agente.

### MongoDB y datos de la entrega

```powershell
docker run -d --name mongo-iot -p 27017:27017 -v mongo-iot-data:/data/db mongo:8
docker cp Docs\Scripts\01_crear_objetos.js mongo-iot:/tmp/01.js
docker cp Docs\Scripts\02_cargar_datos.js mongo-iot:/tmp/02.js
docker exec mongo-iot mongosh --quiet --file /tmp/01.js
docker exec mongo-iot mongosh --quiet --file /tmp/02.js
```

Los scripts JS viven en `Docs/Scripts/` y **no se versionan** por la regla
`/Scripts` de `Docs/.gitignore`. Si clonas el repo, pídelos al equipo. Sin ellos
no se puede recrear `teiba_db` desde cero.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
copy .env.example .env
# Edita backend\.env y define OPENCODE_API_KEY
.\.venv\Scripts\python.exe -m app.scripts.seed_demo
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Checks

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.scripts.check_health
.\.venv\Scripts\python.exe -m app.scripts.check_model
.\.venv\Scripts\python.exe -m app.scripts.smoke_demo
```

`check_health` verifica el endpoint; `check_model` hace una consulta acotada al
modelo; `smoke_demo` valida las dos consultas de la demo.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

El scaffold abre en `http://localhost:5173`, pero todavía muestra el template de
Vite. La UI final se implementa después de los prototipos. Cuando exista,
consumirá `http://127.0.0.1:8000` mediante `VITE_API_URL`.

### Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q -m integration
.\.venv\Scripts\python.exe -m ruff check .
```

### Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `503 llm_not_configured` | Falta la key | `backend/.env` y reiniciar |
| `503 db_unavailable` | Mongo caído | `docker start mongo-iot` |
| `429 rate_limited` | Límite por minuto/concurrencia | Esperar `Retry-After` |
| `502 llm_unavailable` | OpenCode Go no responde | Reintentar |
| `504 timeout` | Consulta compleja | Simplificar |
| `items: []` en sensores | Mongo sin dispositivos | Ejecutar `01` y `02` |
| “No tengo datos” | Seed viejo o no ejecutado | `seed_demo` |

## 11. Estado, verificación y pendientes

### Snapshot

| Campo | Valor |
|---|---|
| Fecha | 2026-10-24 |
| Último commit funcional verificado | `2239f47` |
| Guía de Postman | `99910a7` |
| Contexto consolidado | `938b0ef` |
| Entrega 3 (spec) | `8f1ca72` |
| Tests | 76 passed |
| Lint | `ruff` limpio |
| Frontend | Scaffold, sin UI |
| Mongo | `mongo-iot` con `teiba_db` y 217 lecturas demo |
| Entrega 3 (Word) | Generado localmente; no se versiona por `.gitignore` |

### Criterios de la spec 002

| N.º | Criterio | Estado |
|---|---|---|
| 1 | Contrato de esquema contra `ModeloDatos.md` | ✅ registrado |
| 2 | Seed con lecturas frescas | ✅ registrado |
| 3 | Health con Mongo y LLM | ⏳ falta `OPENCODE_API_KEY` |
| 4 | Consulta principal con 3 trazas | ⏳ falta `OPENCODE_API_KEY` |
| 5 | Backend probado | ✅ registrado |
| 6 | Frontend compila y prueba | ⏳ UI pausada |
| 7 | Seguridad sin key ni stack | ✅ registrado |
| 8 | Contexto alineado y docs | ⏳ `check_docs` pendiente |

### Historial de creación

| Commit | Mensaje |
|---|---|
| `c6009a3` | `docs: incorporar documentación base y modelo de datos del proyecto` |
| `49aa6e2` | `docs: registrar especificación y ADR del panel Sage` |
| `2eb4f0c` | `feat: definir dominio, puertos y repositorios MongoDB` |
| `e179dbb` | `feat: implementar herramientas del agente con validación` |
| `fb4afc9` | `feat: implementar cliente LLM y bucle del agente` |
| `15a4bb6` | `feat: configurar API FastAPI y exponer endpoints del agente` |
| `2632f71` | `feat: añadir datos de demostración y scripts de verificación` |
| `be5ad0c` | `chore: crear scaffold inicial del frontend con Vite` |
| `247136a` | `test: cubrir controles de seguridad de la API` |
| `17a4362` | `docs: ajustar comandos de verificación al entorno virtual` |
| `2239f47` | `docs: registrar verificación del backend en la bitácora` |
| `99910a7` | `docs: añadir guía de Postman para probar la API` |
| `938b0ef` | `docs: consolidar el contexto completo del proyecto` |
| `8f1ca72` | `docs: registrar entrega 3 en la spec` |

Este documento se añade en un commit posterior y no cambia el estado técnico.

### Pendientes

1. Definir `OPENCODE_API_KEY` y validar `check_model`/`smoke_demo`.
2. Recibir los prototipos de diseño.
3. Implementar Tailwind, tokens, cliente API y componentes.
4. Crear `check_docs.py` para el criterio 8 de la spec 002.
5. Corregir la errata del Word sobre el esquema de lecturas.
6. Decidir si los scripts JS se versionan o siguen locales.
7. Opcional: ampliar el panel a las otras cuatro colecciones.
8. Subir a TEMA el Word de la Entrega 3 (`PROYECTO_CURSO_ENTREGA3.docx`) y los
   scripts `01`/`02`/`03`; si la plataforma exige `.doc`, convertir en Word.

## 12. Repositorio y convenciones

### Remoto y rama

- URL: `https://github.com/darman-prog/Teiba.git`.
- Rama: `main`.
- Commits con Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`,
  `chore:`).
- No se hace force-push.
- Cada paso del plan es una unidad de commit.

### `.gitignore` y archivos excluidos

- `Docs/.gitignore` es del equipo: ignora `/Scripts`, `/media`, `/Guia`,
  `/Entregas`, `/Entregables` y `/Contexto`.
- `Docs/Diseno/.gitignore` es del equipo: ignora los generadores y el `.drawio`.
- `frontend/.gitignore` viene del scaffold de Vite.
- El `.gitignore` de la raíz cubre `.venv`, cachés, `.env`, `node_modules` y
  `dist`.
- `DocumentoBase.*` se excluye con `.git/info/exclude`; no está en el remoto.
- No se modifican los `.gitignore` al consolidar este contexto.

### Ignorados importantes

- `Docs/Contexto/`: documentos históricos locales, no versionados.
- `Docs/Scripts/`: scripts JS de la entrega, locales, no versionados.
- `Docs/Entregables/`, `Docs/Entregas/`, `Docs/Guia/`, `Docs/media/`: material
  de curso, no versionado.
- `backend/.env`, `backend/.venv`, `frontend/node_modules`, `frontend/dist`.

### Secretos

- Ningún secreto se versiona.
- `OPENCODE_API_KEY` vive solo en `backend/.env`.
- Los ejemplos usan nombres de variables, no valores.
- El token de GitHub no se documenta.

## 13. Fuentes de verdad y mantenimiento

| Tema | Archivo canónico | Qué manda |
|---|---|---|
| Modelo de datos | [ModeloDatos.md](Docs/Diseno/ModeloDatos.md) | Colecciones, campos, tipos, relaciones |
| Arquitectura | [ADR 002](Docs/adr/002-stack-fastapi-react.md) | Stack, capas, RAG, consecuencias |
| Base única | [ADR 001](Docs/adr/001-mongodb-como-base-unica.md) | MongoDB como motor único |
| Spec y estado | [Spec 002](Docs/features/002-agente-sage-panel.md) | Criterios y bitácora |
| Índice | [INDEX](Docs/features/INDEX.md) | Features activas y cerradas |
| Entregables del curso | [Feature 001](Docs/features/001-entregables-proyecto-curso.md) | E2, E3 y documento final |
| Comandos | [README](README.md) | Arranque y operación |
| Pruebas HTTP | [Guía Postman](Docs/API/README.md) | Endpoints, ejemplos y errores |
| Contexto consolidado | `CONTEXT.md` | Entrada única; no duplica el detalle |

Reglas de mantenimiento:

1. Si cambia un hecho canónico, se actualiza primero el archivo de su fila.
2. Después se actualiza el resumen de `CONTEXT.md` y su fecha.
3. No se copian secretos ni valores de `.env`.
4. No se duplica el schema completo, el ADR completo ni la spec completa.
5. Los documentos históricos de `Docs/Contexto/` no se usan como verdad vigente.
6. Si un enlace relativo deja de existir, se corrige en el mismo cambio.

## 14. Erratas y decisiones descartadas

Esta sección es la única donde se permite mencionar los términos obsoletos. Si
aparecen fuera de aquí, el documento está mal.

- **`parque_iot`**: nombre de base usado en documentos antiguos. La base real es
  `teiba_db` (`Docs/Scripts/01_crear_objetos.js` y ADR 001).
- **SS-03 / Sector Norte**: ejemplo antiguo. El caso canónico es **SS-01 /
  SEC-001**, confirmado por `ModeloDatos.md` §3.3. SS-03 está en SEC-004.
- **`mediciones` anidado**: el Word de la Entrega 2 muestra un subdocumento
  `mediciones`. El modelo canónico y los scripts usan campos planos en la raíz
  de `lecturas`. La app sigue el modelo plano; el Word requiere errata.
- **GraphRAG / Neo4j**: arquitectura explorada al inicio y descartada. No hay
  grafo, ni Cypher, ni `$graphLookup` en la demo.
- **RAG vectorial / embeddings**: descartado. La recuperación es por tools
  deterministas, no por similitud.
- **Kimi / GLM**: no se prueban por costo. Solo DeepSeek y LongCat 2.0.
- **`Docs/Contexto/`**: cuatro documentos históricos, ignorados por Git. No son
  fuente de verdad.
- **`DocumentoBase`**: documento local del curso, excluido con
  `.git/info/exclude`; no se versiona.
- **`Docs/Scripts/`**: scripts JS locales, ignorados por `/Scripts`; no están en
  el remoto.
- **`sector_id` en la guía de Postman**: el ejemplo muestra `SEC-001`, pero el
  DTO devuelve el ObjectId como string. El código legible aparece en
  `sector_codigo` de las tools.

## 15. Glosario

| Término | Significado |
|---|---|
| **RAG por herramientas** | El LLM pide datos con tools; el backend recupera de Mongo y aumenta el contexto antes de generar |
| **Tool calling** | El modelo devuelve una llamada a función con nombre y argumentos JSON |
| **Traza** | Registro de una tool invocada: nombre, argumentos, duración y resultado |
| **Time-series** | Colección MongoDB optimizada para datos con marca temporal |
| **BSON** | Formato binario de MongoDB; incluye ObjectId, Date, Double, Int32 |
| **ObjectId** | Identificador de 12 bytes usado por parques y sectores |
| **Embedding / referencing** | Guardar un subdocumento dentro de otro o referenciar por `_id` |
| **Monolito modular** | Un solo despliegue con módulos y límites internos claros |
| **SPA** | Aplicación de una sola página que consume una API |
| **Seed** | Datos sintéticos para desarrollo y demo |
| **Staleness** | Antigüedad de la última lectura; si supera 60 min, el sensor no reporta |
| **traceId** | Identificador de una petición para correlacionar logs y errores |
| **Grounding** | Obligación de responder solo con datos recuperados |

## 16. Preguntas abiertas y próximos pasos

1. **Modelo y key**: definir `OPENCODE_API_KEY` y verificar el ID exacto de
   DeepSeek en `/models`; si falla, usar LongCat 2.0.
2. **Prototipos**: recibir los frames de diseño y validar la dirección visual.
3. **Frontend**: instalar Tailwind 4, tokens, cliente API y componentes; añadir
   `typecheck`, `test` y `build` al `package.json`.
4. **Cierre**: crear `check_docs.py`, alinear el contexto y cerrar la spec 002.
5. **Word**: corregir la errata del esquema de lecturas antes de la entrega
   final.
6. **Scripts JS**: decidir si se versionan o se mantienen locales; no se toca el
   `.gitignore` sin acuerdo.
7. **Alcance futuro**: valorar una vista de mantenimientos e incidentes con las
   otras cuatro colecciones.

Cuando el frontend esté implementado, este archivo debe actualizar su sección 8,
su sección 11 y su fecha.
