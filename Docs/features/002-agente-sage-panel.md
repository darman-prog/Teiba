---
id: 002
status: en-curso
area: backend
tarea: -
created: 2026-10-24
updated: 2026-10-24
---
# Feature 002 — Agente Sage y panel de monitoreo

## Objetivo
Construir el panel de Sage con chat, trazas y estado de sensores, sobre datos sintéticos frescos y el modelo canónico de `ModeloDatos.md`.

## Contexto
La feature 001 excluyó backend/panel (`Docs/features/001-entregables-proyecto-curso.md:24`).
El contexto usa `parque_iot` y un ejemplo SS-03/Sector Norte que no coincide con los datos; los scripts usan `teiba_db`, `lecturas` planas y fechas fijas que dejan la ventana vacía.
`ModeloDatos.md` §3.1/§3.3 es la fuente canónica; el `mediciones` de `ExplicacionEntrega2.md:153` es errata.
El RAG es el bucle del agente, no un nodo de despliegue: recuperación en tools/repositorios, aumentación en el bucle y generación en OpenCode Go.
Modelos: DeepSeek (principal) y LongCat 2.0 (respaldo); Kimi y GLM se descartan por costo.

## Alcance
| Incluye | Excluye |
|---|---|
| FastAPI, 4 tools, bucle, seed, panel React, tests, ADR 002 | Neo4j, embeddings, auth, gráficas, despliegue, Word, otras 4 colecciones |

## Criterios de aceptación
| N.º | Criterio verificable | Comando | Evidencia |
|---|---|---|---|
| 1 | Contrato de esquema contra `ModeloDatos.md` | `cd backend && .venv\Scripts\python.exe -m pytest tests/integration/test_schema_contract.py -q` | exit 0 |
| 2 | Seed inserta lecturas frescas | `cd backend && .venv\Scripts\python.exe -m app.scripts.seed_demo` | exit 0 + conteo |
| 3 | Health reporta Mongo y LLM | `cd backend && .venv\Scripts\python.exe -m app.scripts.check_health` | JSON |
| 4 | Consulta principal responde SS-01 con 3 trazas | `cd backend && .venv\Scripts\python.exe -m app.scripts.smoke_demo` | exit 0 |
| 5 | Backend probado | `cd backend && .venv\Scripts\python.exe -m pytest -q` | exit 0 |
| 6 | Frontend compila y prueba | `cd frontend && npm run typecheck && npm run lint && npm run test -- --run && npm run build` | exit 0 |
| 7 | Seguridad: sin key ni stack | `cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_security.py -q` | exit 0 |
| 8 | Contexto alineado y docs persistidos | `cd backend && .venv\Scripts\python.exe -m app.scripts.check_docs` | exit 0 |

## Pasos
1. Persistir spec y ADR — `docs: registrar spec y ADR del panel Sage`
2. Base FastAPI, config, errores, CORS, rate limit — `feat: configurar API FastAPI y contrato de errores`
3. Repositorios, rangos y contrato de esquema — `feat: repositorios MongoDB y evaluación de rangos`
4. Tools y validación — `feat: herramientas del agente con validación de argumentos`
5. LLM y bucle del agente — `feat: bucle del agente con tool calling y caché`
6. Endpoints del agente y catálogo — `feat: endpoints del agente y catálogo de sensores`
7. Seed de demo y smoke test del modelo — `feat: seed de lecturas recientes para la demo`
8. Base del frontend — `feat: base del panel React y cliente de API`
9. Chat, trazas y estados — `feat: chat, trazas y tira de sensores`
10. E2E, contexto y cierre — `docs: alinear contexto y cerrar la spec del panel Sage`

## Bitácora
| Criterio | Fecha | Comando | Exit | Commit |
|---|---|---|---|---|
| 1 | 2026-10-24 | cd backend && .venv\Scripts\python.exe -m pytest tests/integration/test_schema_contract.py -q | 0 | 17a4362 |
| 2 | 2026-10-24 | cd backend && .venv\Scripts\python.exe -m app.scripts.seed_demo | 0 | 17a4362 |
| 5 | 2026-10-24 | cd backend && .venv\Scripts\python.exe -m pytest -q | 0 | 17a4362 |
| 7 | 2026-10-24 | cd backend && .venv\Scripts\python.exe -m pytest tests/api/test_security.py -q | 0 | 17a4362 |

## Rollback
Borrar `backend/` y `frontend/`; `mongosh teiba_db --eval 'db.lecturas.deleteMany({"meta.origen":"demo"})'`;
revertir `Docs/Contexto` con git. No se tocan `Scripts/` ni el Word.

## Cierre
- Fila resumen del changelog: "Panel Sage con FastAPI/React, tools sobre `teiba_db` y seed de demo verificado".
- Decisión de arquitectura: ADR 002.
