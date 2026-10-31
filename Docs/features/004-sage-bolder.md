# 004 — Bolder artístico del panel Sage

Objetivo: subir expresión del panel Sage sin salir del mundo “Estación de campo”.
Alcance: bitácora, ruta de la señal, transecto, composer. Excluye: libro, shell, backend.

## Criterios

1. `critique` con veredicto escrito — evidencia: `.impeccable/critique/2026-10-28T00-24-42Z__frontend-src-features-agent-sageview-tsx.md` (24/40, Acceptable)
2. `npm run build` exit 0 — evidencia: log del comando
3. `npm run test -- --run` + axe en verde — evidencia: 28/28, `App.axe.test.tsx` incluido
4. `detect frontend/src` exit 0 o ignores justificados — evidencia: `[]`, sin ignores
5. Capturas desktop+mobile — evidencia: pendiente de verificación manual (sin navegador en el harness)

## Bitácora

| Fecha | Comando | Exit | Commit |
|---|---|---|---|
| 2026-10-28 | `impeccable critique-storage` + trend (dual-agent A/B) | 0 | - |
| 2026-10-28 | `npm run typecheck`, `npm run lint`, `npm run test -- --run` (28/28) | 0 | - |
| 2026-10-28 | `npm run build` | 0 | - |
| 2026-10-28 | `npm run detect:ui` (`[]`) | 0 | - |

## Cambios

- Un solo hilo copper: iconos Wrench/Route y diamante pasan a moss; el cobre vive solo en `.signal-rail`.
- Respuesta Sage a 15px con `max-w-prose`; readout del transecto `05 nodos · N en revisión`.
- P0: tarjeta sin `aria-label` enmascarador; `sr-only` + `aria-describedby` a sector y lectura.
- P1: ruta colapsada en móvil hasta haber selección; `aria-live` solo en la última respuesta.
- P2: `key={message.id}` en `SignalPath`; pill mongo siempre visible; texto en Actualizar.
- Hardening: copiar args+resultado en `SignalDetail`; Ctrl/Cmd+Enter; glosa del `traceId`; hint con mínimo de 3.

## Riesgos

- Detector sobre decisiones expresivas: resuelto sin ignores (salida `[]`).
- Scope-creep al libro: no tocado; solo tokens compartidos ya existentes.
- Pulido infinito: techo de 2 rondas; capturas manuales pendientes del usuario.

## Rollback

`git revert` por paso; este cambio es un único commit.
