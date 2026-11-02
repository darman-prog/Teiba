# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Operador de parques del área metropolitana de Bucaramanga: pregunta por el
estado de sensores IoT sin conocer IDs ni colecciones, en una demo local.
El operador de mantenimiento recibe tareas asignadas, las inicia y las cierra
con una nota. El profesor evaluador es audiencia secundaria: verifica datos
reales y trazas auditables. El desarrollador reproduce la demo desde el repo.

## Product Purpose

Teiba permite monitorear parques urbanos y sus dispositivos IoT con lenguaje
natural. Sage responde sobre sensores usando solo herramientas de solo lectura
contra MongoDB (`teiba_db`) y muestra cada tool invocada con argumentos y
tiempos. El éxito es una respuesta trazable en ≤3 interacciones, verificable
contra datos reales y seed con anomalías controladas.

## Positioning

RAG por herramientas, no por vectores: recuperación determinista, evaluación
de rangos en el dominio y trazas visibles. Ningún vecino académico puede
copiar la trazabilidad tool-por-tool sin el mismo circuito
MongoDB → FastAPI → LLM → FastAPI.

## Operating Context

Demo local académica (Bases de Datos II, UNAB): Vite en `:5173`, FastAPI en
`:8000`, MongoDB en `:27017`, todo en `127.0.0.1`. Auth local por cookie
(ADR 003), sin registro público, sin tráfico real y sin exposición a LAN. La
key del LLM vive solo en `backend/.env`. Flujo de la demo en `CONTEXT.md` §3;
contrato HTTP en §7.

## Capabilities and Constraints

El panel Sage ofrece tira de 5 sensores de suelo, chat con Sage, ruta de la
señal por respuesta, estados empty/loading/error/success, libro de parques de
solo lectura y una vista de mantenimientos: el admin asigna, reasigna, finaliza
casos externos y reabre con nota; el operador inicia y finaliza solo sus tareas.
Terminología del contrato: `snake_case`, `trazas[]`, `meta.trace_id`, `traceId`
en errores. Sin CRUD de parques, sectores, inventario ni usuarios; los
incidentes y el inventario se leen para vincular tareas. Sin mapas, gráficas
históricas ni actuadores. Rate limit: 10 POST/min por IP, 2 concurrentes. Pregunta de
3–500 caracteres. Decisiones abiertas: ninguna material pendiente.

## Brand Commitments

Nombre Teiba · Sage y claim “hilos de datos, parques vivos”. Mundo visual
“Estación de campo” confirmado por el usuario; nada de sus elementos es
intocable salvo el mundo mismo. Sin logo, sin assets de marca adicionales.

## Evidence on Hand

Seed `backend/app/scripts/seed_demo.py` (217 lecturas, anomalías SS-01/SS-02/
SS-03/MET-01). Prototipos HTML de referencia en
`Docs/PrototiposFrontend/teiba-sage/` (históricos; la fuente vigente es el
código React). Contrato en `Docs/API/README.md`. Tests: 76 backend, suite
Vitest + axe en `frontend/src`.

## Product Principles

1. Grounding antes que elocuencia: toda afirmación sale de una tool.
2. Trazabilidad visible: cada respuesta muestra su ruta de la señal.
3. Operar, no decorar: la UI desaparece detrás de la tarea del operador.
4. Demo reproducible: mock o backend real, mismos estados, mismos tests.

## Accessibility & Inclusion

WCAG 2.2 AA. Teclado completo, foco visible, `aria-live` en chat/carga/error,
contraste AA, objetivos táctiles 44×44 en móvil, `prefers-reduced-motion`.
