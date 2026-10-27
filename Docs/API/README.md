# Guía rápida: probar la API de Teiba con Postman

Esta guía sirve para levantar el backend, hacer peticiones HTTP desde Postman y
entender qué devuelve cada endpoint. Léela antes de probar la API; los ejemplos
usan los datos de la demo y la colección incluida en `Docs/API/postman/`.

## 1. Antes de empezar

Necesitas MongoDB con los datos de la entrega, el seed de demo y el backend en
ejecución. Desde la raíz del repo:

```powershell
# 1. MongoDB (si no está corriendo)
docker start mongo-iot

# 2. Lecturas frescas para la demo
cd backend
.\.venv\Scripts\python.exe -m app.scripts.seed_demo

# 3. API en localhost
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Para probar el agente necesitas una `OPENCODE_API_KEY` válida en
`backend/.env`. Esa clave es del backend hacia OpenCode Go, **no** es un token
que se envíe desde Postman.

Comprueba que la API responde:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health | ConvertTo-Json -Depth 5
```

También puedes abrir:

- `http://127.0.0.1:8000/docs` — Swagger UI.
- `http://127.0.0.1:8000/openapi.json` — contrato OpenAPI que Postman puede importar.

## 2. Postman en 5 minutos

1. Instala **Postman Desktop**. Si usas Postman web, necesitas el **Desktop
   Agent** para llegar a `localhost`; el CORS del backend no afecta a Postman
   Desktop.
2. Crea un workspace y una colección, o importa la colección de este repo.
3. Crea el environment `Teiba Local` con la variable
   `baseUrl = http://127.0.0.1:8000` y selecciónalo arriba a la derecha.
4. Importa los archivos:
   - **Recomendado:** `Import > Files` →
     `Docs/API/postman/Teiba-Sage.postman_collection.json` y
     `Docs/API/postman/Teiba-Local.postman_environment.json`.
   - **Alternativa:** `Import > Link` → `http://127.0.0.1:8000/openapi.json` y
     genera una colección. Las requests generadas no incluyen los tests ni los
     ejemplos de esta guía.
5. Abre `Teiba Sage API > Salud > Health` y pulsa **Send**.

### Anatomía de una request

| Parte | Qué poner |
|---|---|
| Método | `GET` para consultar, `POST` para el agente |
| URL | `{{baseUrl}}/api/...` |
| Params | Query string, por ejemplo `tipo` y `limite` |
| Headers | `Content-Type: application/json` solo en POST; `X-Request-Id` es opcional |
| Body | `raw` + `JSON` para `POST /api/agente/consulta` |
| Tests | Pestaña **Tests**; la colección ya trae validaciones básicas |
| Send | `Ctrl + Enter` en Windows |

La variable `{{baseUrl}}` viene del environment. Si cambias el puerto, edita el
environment y no cada request. No guardes secretos en Postman.

## 3. Endpoints y contrato

La API no tiene autenticación y escucha en `127.0.0.1`. Todos los campos usan
`snake_case`, salvo el `traceId` del contrato de errores.

| Método | Ruta | Entrada | Éxito | Errores |
|---|---|---|---|---|
| `GET` | `/api/health` | — | 200 con `status`, `mongo`, `llm`, `version` | 500 no controlado |
| `GET` | `/api/sensores` | `tipo`, `limite` | 200 con `items[]` y `total` | 422, 503 `db_unavailable` |
| `POST` | `/api/agente/consulta` | `{"pregunta": "..."}` | 200 con `respuesta`, `trazas[]`, `meta` | 422, 429, 502, 503, 504 |
| `GET` | `/docs`, `/redoc`, `/openapi.json` | — | HTML/JSON | — |

Parámetros de `/api/sensores`:

| Parámetro | Valores | Por defecto |
|---|---|---|
| `tipo` | `calidad_suelo`, `estacion_meteorologica`, `luminaria_inteligente`, `antena_enlace` | `calidad_suelo` |
| `limite` | Entero de 1 a 50 | `50` |

Notas del contrato:

- `total` es la cantidad de ítems devueltos, no el total de la colección. No
  hay paginación: sube `limite` hasta 50.
- La API no pide `Authorization`; la `OPENCODE_API_KEY` vive en `backend/.env`.
- Los errores usan `{code, message, details, traceId}`. `details` puede ser
  `null`, una lista (422) o un objeto (429). El campo `traceId` va en camelCase.

### Headers útiles

| Header | Dirección | Uso |
|---|---|---|
| `Content-Type: application/json` | Request | Obligatorio en el POST del agente |
| `X-Request-Id` | Request | Opcional; se convierte en el `trace_id` de la respuesta |
| `X-Trace-Id` | Response | Siempre presente; sirve para correlacionar logs |
| `Retry-After` | Response | Segundos de espera cuando llega un 429 |

## 4. Ejemplos de uso

### 4.1 Health

```
GET {{baseUrl}}/api/health
```

Respuesta sana:

```json
{
  "status": "ok",
  "mongo": { "ok": true, "db": "teiba_db" },
  "llm": { "configurado": true, "modelo": "deepseek-v4.1-flash" },
  "version": "0.1.0"
}
```

El endpoint devuelve 200 incluso cuando algo falla: hay que leer el body.

| Campo | Significado |
|---|---|
| `status` | `ok` solo si Mongo y el LLM están listos; si no, `degraded` |
| `mongo.ok` | `false` si MongoDB no responde |
| `llm.configurado` | `false` si falta `OPENCODE_API_KEY` o está vacía |

Test para la pestaña **Tests**:

```js
pm.test("200 OK", () => pm.response.to.have.status(200));
const body = pm.response.json();
pm.test("Mongo responde", () => pm.expect(body.mongo.ok).to.eql(true));
pm.test("Base teiba_db", () => pm.expect(body.mongo.db).to.eql("teiba_db"));
```

### 4.2 Sensores

```
GET {{baseUrl}}/api/sensores?tipo=calidad_suelo&limite=5
```

Respuesta ilustrativa con el seed de demo (los valores exactos pueden variar):

```json
{
  "items": [
    {
      "id": "SS-01",
      "tipo": "calidad_suelo",
      "marca": "SoilPro-Sense LoRa",
      "sector": "Sector Norte - Jardines de la Escultura de Botero",
      "sector_id": "SEC-001",
      "parque": "Parque San Pío",
      "comuna": "Comuna 12 - Cabecera del Llano",
      "depende_de": "ANT-01",
      "alimentado_por": "Panel_Solar_PS1",
      "ultima_lectura": {
        "timestamp": "2026-10-27T14:30:00Z",
        "humedad": 41.2,
        "ph": 5.4,
        "temperatura": 21.0,
        "bateria": 90,
        "antiguedad_min": 15
      },
      "estado": "danger"
    }
  ],
  "total": 1
}
```

Interpretación:

- `estado` puede ser `ok`, `warning`, `danger` o `sin_datos`.
- `danger` tiene prioridad sobre `warning`.
- Con el seed: SS-01 sale `danger` por pH 5.4, SS-02 `warning` por llevar 7 h
  sin reportar y SS-03 `danger` por batería 15 %.
- `ultima_lectura` puede ser `null` si el dispositivo nunca ha reportado.
- `seed_demo` solo inserta lecturas de `calidad_suelo`; MET-01 y LUM-01 pueden
  salir `sin_datos`. Las antenas tampoco reportan telemetría ambiental.

Variantes listas para copiar:

```
GET {{baseUrl}}/api/sensores
GET {{baseUrl}}/api/sensores?tipo=estacion_meteorologica&limite=5
GET {{baseUrl}}/api/sensores?tipo=antena_enlace&limite=5
GET {{baseUrl}}/api/sensores?tipo=luminaria_inteligente&limite=5
```

Pruebas de validación:

```
GET {{baseUrl}}/api/sensores?limite=0    -> 422 invalid_request
GET {{baseUrl}}/api/sensores?tipo=otro   -> 422 invalid_request
```

### 4.3 Agente

```
POST {{baseUrl}}/api/agente/consulta
Content-Type: application/json
X-Request-Id: prueba-001
```

Body:

```json
{
  "pregunta": "¿Cómo está el sensor de calidad del suelo del Sector Norte?"
}
```

Respuesta resumida:

```json
{
  "respuesta": "El sensor SS-01 del Sector Norte ... pH 5.4, fuera del rango ...",
  "trazas": [
    {
      "tool": "list_sensors",
      "args": { "tipo": "calidad_suelo", "sector": "Sector Norte" },
      "ok": true,
      "ms": 3,
      "resumen": "1 dispositivos",
      "resultado": "{\"estado\": \"ok\", ...}"
    }
  ],
  "meta": {
    "modelo": "deepseek-v4.1-flash",
    "pasos": 3,
    "duracion_ms": 4200,
    "cached": false,
    "trace_id": "prueba-001"
  }
}
```

Detalles importantes:

- `trazas[].resultado` es un **string JSON truncado** (`TOOL_RESULT_MAX_CHARS`),
  no un objeto.
- `meta.cached` es `true` si repites la misma pregunta dentro de
  `DEMO_CACHE_TTL_SECONDS` (600 s por defecto).
- `meta.trace_id` es el `X-Request-Id` que enviaste; si no enviaste ninguno, se
  genera uno.
- La consulta puede tardar hasta 60 s (`AGENT_TOTAL_TIMEOUT_SECONDS`).
- Si el modelo no usa herramientas, el backend lo obliga a intentarlo de nuevo;
  por eso `meta.pasos` puede ser mayor que 1.

Segunda consulta de la demo:

```json
{
  "pregunta": "¿Qué sensores dependen de la antena ANT-01 y alguno está sin reportar?"
}
```

Debe mostrar trazas de `get_devices_by_antenna` e identificar SS-02 como
`sin_reportar`.

Test para la consulta principal:

```js
pm.test("200 OK", () => pm.response.to.have.status(200));
const body = pm.response.json();
pm.test("Respuesta no vacía", () => pm.expect(body.respuesta).to.be.a("string").and.not.empty);
pm.test("Trazas es array", () => pm.expect(body.trazas).to.be.an("array"));
pm.test("Meta completa", () => {
  pm.expect(body.meta).to.include.keys("modelo", "pasos", "duracion_ms", "cached", "trace_id");
});
```

### 4.4 Errores

Contrato único:

```json
{
  "code": "invalid_request",
  "message": "Los datos enviados no son válidos.",
  "details": [
    {
      "loc": ["body", "pregunta"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ],
  "traceId": "..."
}
```

| HTTP | `code` | Cuándo ocurre | Qué hacer |
|---|---|---|---|
| 422 | `invalid_request` | Query o body inválido | Revisa `details[].loc` |
| 429 | `rate_limited` | Más de 10 consultas/min o 2 concurrentes | Espera `Retry-After` |
| 502 | `llm_unavailable` | OpenCode Go no responde | Reintenta |
| 503 | `llm_not_configured` | Falta la key o es inválida | Configura `backend/.env` y reinicia |
| 503 | `db_unavailable` | MongoDB caído | Arranca el contenedor `mongo-iot` |
| 504 | `timeout` | La consulta superó el tiempo máximo | Simplifica la pregunta |
| 404 | `not_found` | Ruta inexistente | Revisa la URL |
| 500 | `internal_error` | Error no controlado | Busca el `traceId` en el log del servidor |

Ejemplos de cuerpos:

```json
{
  "code": "rate_limited",
  "message": "Demasiadas consultas. Intenta de nuevo en unos segundos.",
  "details": { "retry_after": 12 },
  "traceId": "..."
}
```

```json
{
  "code": "llm_not_configured",
  "message": "La API del agente no está configurada. Define OPENCODE_API_KEY.",
  "details": null,
  "traceId": "..."
}
```

```json
{
  "code": "db_unavailable",
  "message": "La base de datos no está disponible.",
  "details": null,
  "traceId": "..."
}
```

El 400 `Invalid host header` no usa este contrato: lo genera el middleware de
hosts permitidos. Usa `127.0.0.1` o `localhost`, o agrega el host a
`ALLOWED_HOSTS`.

## 5. Rate limit y buenas prácticas

El límite aplica **solo** a `POST /api/agente/consulta`:

- 10 peticiones por minuto por IP.
- 2 consultas concurrentes.
- Ventana deslizante de 60 s; el 429 incluye `Retry-After`.

Para probarlo:

1. Envía 11 consultas seguidas y observa el 429.
2. O lanza 3 consultas simultáneas: la tercera recibe “El agente está ocupado”.

No ejecutes el agente en bucle: consume tokens, tarda y gasta el rate limit. El
límite es en memoria y de un solo proceso; no es una protección de producción.
No expongas esta API a Internet: no tiene autenticación.

## 6. Problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ECONNREFUSED 127.0.0.1:8000` | API apagada o puerto ocupado | Arranca uvicorn; revisa el puerto |
| `400 Invalid host header` | URL con IP de LAN, `0.0.0.0` o dominio no permitido | Usa `127.0.0.1`/`localhost` o edita `ALLOWED_HOSTS` |
| `422 invalid_request` | Query o body inválido | Revisa `details[].loc` |
| `503 db_unavailable` | MongoDB caído | `docker ps`; arranca `mongo-iot` |
| `503 llm_not_configured` | Falta `OPENCODE_API_KEY` | Edita `backend/.env` y reinicia la API |
| `429 rate_limited` | Límite por minuto o concurrencia | Espera `Retry-After` |
| `502 llm_unavailable` | OpenCode Go no responde | Reintenta |
| `504 timeout` | Consulta demasiado compleja | Simplifica la pregunta |
| Postman web no llega a localhost | CORS/agente cloud | Usa Postman Desktop o Desktop Agent |
| `items: []` en sensores | Mongo sin `dispositivos` | Ejecuta `01_crear_objetos.js` y `02_cargar_datos.js` |

## 7. Referencias

- Colección: `Docs/API/postman/Teiba-Sage.postman_collection.json`.
- Environment: `Docs/API/postman/Teiba-Local.postman_environment.json`.
- Swagger: `http://127.0.0.1:8000/docs`.
- OpenAPI: `http://127.0.0.1:8000/openapi.json`.
- Contrato y código: `backend/app/api/health.py`, `sensors.py`, `agent.py`,
  `schemas.py`, `errors.py` y `middleware.py`.
- Spec de la feature: `Docs/features/002-agente-sage-panel.md`.
