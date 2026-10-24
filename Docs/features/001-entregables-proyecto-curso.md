---
id: 001
status: aprobada
created: 2026-10-17
updated: 2026-10-18
area: datos
tarea: -
---
# Feature 001 — Entregables del proyecto de curso (BD II NoSQL)

> Preparar modelo MongoDB de ≥7 entidades, scripts con 10 registros c/u, 5 consultas y documento final, alineando la visión con las decisiones reales del equipo.

## Objetivo
Entregar a la docente: MER Chen + modelo de colecciones + descripción de entidades (E2), scripts ejecutables con 5 consultas (E3) y documento final sin placeholders (Efinal).

## Contexto
El enunciado (`Docs/DocumentoBase.md`) exige ≥7 entidades y 10 registros c/u (`:165`, `:278`) y 5 consultas sobre ≥2 colecciones (`:282`); la implementación actual solo modela 2 colecciones para el agente IoT, y la visión (`Docs/Contexto/IdeaProyectoVision.md`) aún describe GraphRAG + Neo4j, decisión revertida en `Docs/Contexto/contexto-agente-iot-parques.md:28,34`. Entidades base propuestas: `parques`, `sectores`, `dispositivos`, `lecturas`, `elementos_inventario`, `mantenimientos`, `incidentes`, `usuarios` (8, margen sobre el mínimo).

Entregas del curso: E2 (MER + modelo + descripción de entidades), E3 (script objetos + datos + consultas), Efinal (presentación + documento + scripts) según `Docs/Entregas/entrega2.txt`, `entrega3.txt` y `entregaFinal.txt`. Fechas por confirmar.

Naming oficial: proyecto **Teiba** (TE-lar + (C)IBA) con agente **Sage**. La Entrega 1 se tituló «Ceiba»; desde la E2 se usa Teiba (cambio cosmético, sin cambios de alcance). Claim base: «Teiba: hilos de datos, parques vivos».

## Alcance
| Incluye | Excluye |
|---|---|
| Visión alineada, ADR, MER/modelo de colecciones, scripts, 5 consultas, doc final `.md` | Port a `.doc`, presentación PPT, backend/panel del agente, Neo4j real, vectores |

## Criterios de aceptación
| N.º | Criterio verificable | Evidencia |
|---|---|---|
| 1 | `grep -in "graphrag\|neo4j" Docs/Contexto/IdeaProyectoVision.md` → toda mención en "Trabajo futuro"/"Limitaciones" | `Docs/Contexto/IdeaProyectoVision.md` |
| 2 | ADR 001 persistido con Contexto/Decisión/Consecuencias/Alternativas | `Docs/adr/001-mongodb-como-base-unica.md` |
| 3 | Checklist Chen completo (entidades, relaciones, cardinalidad parcial y total, llaves) y ≥7 entidades trazables a `DocumentoBase.md:52-115` | `Docs/Diseno/ModeloDatos.md` |
| 4 | `db.getCollectionNames()` ≥7 colecciones y `lecturas` como time-series | `Scripts/01_crear_objetos.js` |
| 5 | Conteo ≥10 registros por colección | `Scripts/02_cargar_datos.js` |
| 6 | 5 consultas sin error, ≥2 colecciones c/u, con resultado documentado | `Scripts/03_consultas.js` + `Docs/Diseno/Consultas.md` |
| 7 | 0 placeholders (`dd/mm/aaaa`, "Aquí va", "AQUÍ LA IMAGEN") en el documento final | `Docs/Entregables/PROYECTO_CURSO.md` |
| 8 | Documento final con título «Teiba»; `grep -i ceiba` en entregables solo en la nota histórica del cambio de nombre | `Docs/Entregables/PROYECTO_CURSO.md` |

## Pasos
1. Alinear visión (criterio 1) — commit propuesto: `docs: alinear visión con decisión MongoDB única`
2. ADR 001 (criterio 2) — `docs: añadir ADR MongoDB como base única`
3. Modelo de datos (criterio 3, pre-flight `backend-expert`) — `docs: modelo entidades-relaciones y colecciones`
4. Script objetos (criterio 4) — `feat: script creación 8 colecciones`
5. Script datos (criterio 5) — `feat: datos sintéticos 10+ por colección`
6. Consultas (criterio 6) — `feat: 5 consultas sobre múltiples colecciones`
7. Doc final (criterio 7, revisión `auditor`) — `docs: proyecto_curso completo`

## Notas de ejecución
- El proyecto no es repo git: cada paso cierra con su criterio de aceptación; si se hace `git init`, aplican los commits propuestos.
- Pendiente con la docente: confirmar si el diagrama entregable es solo MongoDB (pendiente §9.1 de `Docs/Contexto/contexto-agente-iot-parques.md`) antes del paso 3.
- El diagrama Chen final es imagen: el paso 3 entrega la especificación dibujable en markdown; el dibujo lo porta el usuario.
- Naming: en el Word de la E1 (copia enviada, fuera del repo) reemplazar «Ceiba» por «Teiba»; todo documento nuevo usa Teiba.
- Alcance actual (18/10/2026): **Entrega 2 completada al 100%** (MER Chen formal con elipses de atributos, doble línea y doble contorno, modelo de documentos y tablas BSON inyectadas en `Docs/Entregables/PROYECTO_CURSO_ENTREGA2.docx`, guías operativas en `Docs/Guia/`); pasos de la Entrega 3 (scripts y consultas ya probados) y doc final se retoman según calendario.
- Repo `darman-prog/Teiba` (público, vacío): alojará **solo el software de Teiba y una documentación breve**; se inicializa cuando exista software. No contiene entregas del curso.

## Cierre
- Fila changelog: "Entregables E2/E3/final listos: modelo 8 entidades, scripts y consultas verificados".
- ADR 001 creado en paso 2.
