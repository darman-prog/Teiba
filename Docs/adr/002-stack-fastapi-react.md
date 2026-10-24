# ADR 002: FastAPI + React/Vite/Tailwind para el panel del agente Sage

## Contexto

El panel de Sage no existe y la feature 001 excluyó backend/panel
(`Docs/features/001-entregables-proyecto-curso.md:24`). Se necesita una demo local
con chat, trazas y estado de sensores, mantenible por una persona y defendible ante
el docente. El contrato de datos es `Docs/Diseno/ModeloDatos.md` §3.1/§3.3:
8 colecciones, `lecturas` time-series con campos planos y referencias por `ObjectId`.

## Decisión

- Backend FastAPI (Python 3.11+) como **monolito modular por capas**:
  `api → application → domain`, con `infrastructure` implementando puertos.
- `pymongo` síncrono en endpoints `def` (threadpool) y SDK de OpenAI contra OpenCode Go.
- Frontend React 19 + TypeScript + Vite + Tailwind 4, **SPA** organizada en
  `components → hooks → api`, sin librería de componentes.
- MongoDB `teiba_db`; `ModeloDatos.md` es la fuente canónica. El `mediciones`
  anidado de `ExplicacionEntrega2.md:153` es errata documental; el esquema
  operativo es plano.
- Sin autenticación; solo `127.0.0.1`, CORS allowlist y rate limit en memoria.
- El RAG es un patrón interno del backend, no un nodo de despliegue.
- LLM: DeepSeek como modelo principal y LongCat 2.0 como respaldo; Kimi y GLM
  se descartan por costo.

## Arquitectura física

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
no accede a Mongo ni al LLM; FastAPI es el único con credenciales.

## Capas del backend

| Capa | Responsabilidad | Depende de |
|---|---|---|
| `api/` | Routers, DTOs Pydantic, validación, errores, `traceId`, rate limit | aplicación |
| `application/` | Casos de uso: consultar agente, listar sensores, bucle de tools | dominio + puertos |
| `domain/` | Modelos, rangos, evaluación, errores e invariantes | nada (Python puro) |
| `infrastructure/` | Repositorios PyMongo, cliente OpenAI, reloj | implementa puertos |

Regla: `api → application → domain`; `infrastructure` implementa interfaces y se
inyecta en `main.py` (composition root). El dominio no importa FastAPI, PyMongo
ni OpenAI. Puertos: `DeviceRepository`, `ReadingRepository`, `LLMClient`, `Clock`.

## Capas del frontend

| Capa | Responsabilidad | Regla |
|---|---|---|
| `components/` | UI presentacional: chat, trazas, tarjetas | Sin `fetch`, sin reglas de negocio |
| `hooks/` | Estado y casos de uso de pantalla: `useAgent`, `useSensors` | Orquestan el cliente API |
| `api/` | `client.ts`, `agent.ts`, `sensors.ts` | Único lugar con `fetch`, timeout y parseo de errores |
| `types/` | DTOs espejo del contrato OpenAPI | `snake_case`, sin lógica |
| `lib/` | Formato de fechas, números y estados | Funciones puras |

Regla: `components → hooks → api`; `types` y `lib` son hojas compartidas. El
frontend no duplica la evaluación de rangos: esa regla vive en el backend.

## RAG por herramientas

El RAG **no es un nodo separado**. Es el circuito que va de MongoDB a FastAPI,
de FastAPI al LLM y de vuelta a FastAPI. La recuperación vive en las tools y
repositorios; la aumentación, en el bucle del agente; la generación, en OpenCode Go.

```text
┌──────────────────────────── FastAPI ────────────────────────────┐
│                                                                 │
│  api/          routers, DTOs, errores, traceId                   │
│                                                                 │
│  ┌──────────── RAG por herramientas (patrón) ────────────────┐  │
│  │ application/agent/loop.py                                  │  │
│  │   1. envía pregunta + esquemas de tools al LLM             │  │
│  │   2. recibe tool_call                                      │  │
│  │   3. ejecuta la tool contra MongoDB              ← R        │  │
│  │   4. inyecta el resultado en el contexto del LLM ← A        │  │
│  │   5. recibe la respuesta final                   ← G        │  │
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

En un diagrama de despliegue se dibuja como un **recuadro punteado dentro de
FastAPI**, no como una caja aparte. El navegador solo ve la respuesta y las trazas.

### Fases

| Fase | Dónde vive | Qué hace |
|---|---|---|
| **R** — Retrieval | `application/tools` + `infrastructure/repositories` | Consultas deterministas a `lecturas`, `dispositivos`, `sectores` y `parques`; sin embeddings ni similitud |
| **A** — Augmentation | `application/agent/loop.py` | Arma mensajes, ejecuta tools y añade resultados al contexto del LLM |
| **G** — Generation | `infrastructure/llm` + OpenCode Go | Redacta la respuesta usando solo lo recuperado; no consulta Mongo |

`domain/ranges.py` participa en la aumentación: calcula si un valor está fuera de
rango para que el LLM no haga aritmética ni invente criterios.

### Secuencia de una consulta

```text
Operador -> React: "¿Cómo está el suelo del Sector Norte?"
React -> FastAPI: POST /api/agente/consulta
FastAPI -> LLM: system prompt + pregunta + schemas de tools
LLM -> FastAPI: tool_call list_sensors(tipo="calidad_suelo", sector="Sector Norte")
FastAPI -> MongoDB: consulta dispositivos + sectores
MongoDB -> FastAPI: SS-01 / SEC-001
FastAPI -> LLM: resultado de la tool
LLM -> FastAPI: tool_call get_sensor_history("SS-01")
... y así hasta la respuesta final ...
FastAPI -> React: respuesta + trazas
```

Las trazas son la evidencia visible del RAG: muestran qué se recuperó, con qué
argumentos y en qué orden. Sin trazas, el panel sería un chat más.

### Lo que no es

- No es un microservicio aparte: es un patrón dentro del monolito.
- No es RAG vectorial: no hay base de vectores, embeddings ni chunking.
- No es GraphRAG: no hay Neo4j ni recorrido de grafos.
- No es el LLM solo: el LLM genera, pero no accede a la base ni inventa los datos.
- No es el navegador: el cliente solo consume el contrato.

### Defensa

> "El RAG es el patrón de orquestación del backend: recupera datos estructurados
> de MongoDB mediante herramientas deterministas, los inyecta en el contexto del
> LLM y genera una respuesta trazable. El LLM nunca consulta la base; solo recibe
> resultados acotados y validados."

## Consecuencias

### Positivas

- Una sola persona puede construir y sustentar la demo.
- Menos ceremonia que Angular; componentes reutilizables frente a HTML plano.
- El panel hace visible el tool calling y la recuperación aumentada.
- Los puertos permiten probar el agente con LLM/Mongo falsos.

### Negativas

- Sin auth no debe exponerse a LAN.
- El rate limit en memoria no sirve multi-proceso.
- El schema plano contradice el Word hasta la errata documental.

### Mitigaciones

- Bind `127.0.0.1`, CORS exacto, rate limit y caché.
- Documentar la errata de `mediciones` en la entrega final.
- Mantener `ModeloDatos.md` como fuente canónica y un test de contrato de esquema.

## Alternativas descartadas

- **Angular:** sobreingeniería para una demo de un solo panel.
- **HTML simple:** sin componentes, estados ni mantenibilidad.
- **Django DRF:** más configuración y peso para cuatro endpoints.
- **Next.js/SSR:** SSR innecesario para un panel local.
- **Microservicios:** un solo proceso y un solo desarrollador; la red añadiría
  latencia, despliegue y observabilidad sin beneficio.
- **RAG vectorial/GraphRAG:** no hay corpus documental ni grafo; la recuperación
  estructurada por tools es suficiente y verificable.
