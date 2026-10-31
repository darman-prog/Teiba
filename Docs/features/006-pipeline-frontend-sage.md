---
status: en-curso
area: frontend
created: 2026-10-28
updated: 2026-10-28
---
# 006 — Pipeline frontend y pilot SageView

> Sistematizar “Estación de campo” en SageView: dirección, primitivas, showcase y review con capturas.

## Contexto
`Docs/DESIGN.md` ya define el mundo: instrumento de campo, moss/copper, mono tabular, etiquetas Overpass, sin sombras y radios 4–8. El problema no es el mundo; es que el código no lo expresa con un sistema de componentes.

## Dirección elegida
**A. Instrumento de precisión** (elegida): la estación mide y registra. Prioriza densidad legible, ejes, números mono, estados LED y un solo hilo copper para la traza. Es la expresión que ya describe `DESIGN.md`.

## Alternativas
- **B. Bitácora editorial:** más papel/mineral, tipografía grande y notas al margen; menos densidad de panel.
- **C. Panel técnico:** rejilla más densa, estados tipo LED y datos tabulares; más consola, menos narrativa.

## Referencias y anti-referencias
- Referencias: `Docs/DESIGN.md`, prototipos en `Docs/PrototiposFrontend/teiba-sage/` y el panel actual `SageView`.
- Anti-referencias: dashboard SaaS genérico, burbujas de chat, cards con sombra, degradados morados y grids de features idénticas.

## Alcance del pilot
- Una sección de `SageView`: estación + transecto + bitácora + composer. La ruta de señal se revisa, no se reescribe.
- 7 primitivas del sistema: `Button`, `Surface`, `Chip`, `StatusTag`, `EmptyState`, `LoadingState`, `SearchInput`.
- Showcase dev-only en `/showcase`; `check:ui` sobre los archivos tocados.
- Gate: capturas desktop/móvil, axe, `detect:ui`, tests y rating de identidad ≥4/5.

## Gate
Sin capturas no hay review. Si el rating es menor a 4/5, no se propaga ni se podan skills; se ajusta o se abandona el pilot.

Rating: 4/5 (usuario, 2026-10-28). PASS del pilot: capturas en `Docs/evidence/pilot-sage/`; axe 0, tests 32/32, detect `[]`.
