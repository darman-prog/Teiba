---
id: 003
status: cerrada
area: datos
tarea: -
created: 2026-10-27
updated: 2026-10-27
---
# Feature 003 — Entrega 3: implantación y consultas

> Generar `PROYECTO_CURSO_ENTREGA3.docx` (E2 + scripts + 5 consultas) sobre
> `PROYECTO_CURSO_ENTREGA2_FINAL.docx`, con evidencias reales de MongoDB.

## Objetivo
Cumplir `Docs/Entregas/entrega3.txt`: script de objetos (8 colecciones), script
de datos (10+ por entidad) y 5 consultas multicolección, documentados en el
Word del curso con imágenes de ejecución y el anexo de scripts completos.

## Contexto
Los scripts `01_crear_objetos.js`, `02_cargar_datos.js` y `03_consultas.js`
están probados en `Docs/Scripts/` y viven ignorados por `.gitignore`. La
plantilla conserva la tabla de versiones (T001), la tabla de scripts (T007) y
las 5 tablas de consultas (T008–T012) con placeholders `AQUÍ`/`dd/mm/aaaa`.
El seed de demo del panel puede borrarse si se reejecuta `02`.

## Alcance
| Incluye | Excluye |
|---|---|
| Word E3, evidencias PNG, tabla de versiones, anexo A, spec | Conclusiones/IA (Efinal), presentación, Word/scripts en el repo |

## Criterios de aceptación
| N.º | Criterio verificable | Comando | Evidencia |
|---|---|---|---|
| 1 | Datos: 8 colecciones con 10+ registros, índice e invariante | `backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\verificar_datos.py` | exit 0 |
| 2 | Consultas: las 5 devuelven resultados | `backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\verificar_consultas.py` | exit 0 |
| 3 | Evidencias: 7 PNG legibles desde la salida real | `backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\generar_evidencias.py` | exit 0 + 7 PNG |
| 4 | Word: versiones + 2 scripts + 5 consultas con imagen y anexo | `backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\verificar_docx.py` | exit 0 |

## Pasos
1. Capturar salidas reales de 01/02/03 — `feat: evidencias ejecucion scripts entrega 3` (local)
2. Generar PNG con `e3_tools/generar_evidencias.py` — (local)
3. Insertar versiones/9.1/9.2/Anexo A con `insertar_e3.py` — (local)
4. Registrar spec y verificación — `docs: registrar entrega 3 en la spec`

## Bitácora
| Criterio | Fecha | Comando | Exit | Commit |
|---|---|---|---|---|
| 1 | 2026-10-27 | backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\verificar_datos.py | 0 | 938b0ef |
| 2 | 2026-10-27 | backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\verificar_consultas.py | 0 | 938b0ef |
| 3 | 2026-10-27 | backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\generar_evidencias.py | 0 | 938b0ef |
| 4 | 2026-10-27 | backend\.venv\Scripts\python.exe Docs\Entregables\e3_tools\verificar_docx.py | 0 | 938b0ef |

## Rollback
Restaurar `PROYECTO_CURSO_ENTREGA2_FINAL.bak.docx` sobre el Word; borrar
`Docs/Entregables/e3_assets` y `e3_tools/`; si se necesita el panel demo,
reejecutar `seed_demo`. Los `.gitignore` no se tocan.

## Cierre
- Fila resumen del changelog: "Entrega 3 lista: Word con scripts, 5 consultas y evidencias verificadas".
- Decisión de arquitectura: no aplica (entregable de curso).
