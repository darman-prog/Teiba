---
target: panel Sage (SageView)
total_score: 24
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 2
target_identity: "file:C:\\Users\\damez\\Downloads\\Universidad\\quinto_semestre\\BaseDeDatos2\\ProyectoCurso\\Teiba\\frontend\\src\\features\\agent\\SageView.tsx"
target_fingerprint: "sha256:6abb871849cc0fcddab6358421c085a9140c927ef02ea0118a2d83d781bbec17"
target_path: "C:\\Users\\damez\\Downloads\\Universidad\\quinto_semestre\\BaseDeDatos2\\ProyectoCurso\\Teiba\\frontend\\src\\features\\agent\\SageView.tsx"
timestamp: 2026-10-28T00-24-42Z
slug: frontend-src-features-agent-sageview-tsx
---
# Critique: panel Sage (SageView) — Teiba

Method: dual-agent (A: ses_e801cbde · B: ses_e801cbde)

## Design Health Score

| # | Heurística | Score | Issue clave |
|---|---|---|---|
| 1 | Visibilidad del estado del sistema | 3 | En tablet la Ruta oculta el progreso de tools |
| 2 | Coincidencia con el mundo real | 4 | Léxico de campo correcto; `traceId` crudo al operador |
| 3 | Control y libertad del usuario | 2 | "Nueva consulta" borra todo sin confirmar ni deshacer |
| 4 | Consistencia y estándares | 3 | Dos patrones de expansión distintos para trazas |
| 5 | Prevención de errores | 2 | `setDraft('')` optimista con restauración por efecto |
| 6 | Reconocimiento antes que recuerdo | 2 | `aria-label` de la tarjeta enmascara pH/temp/batería |
| 7 | Flexibilidad y eficiencia | 1 | Cero atajos; sugerencias solo precargan, no envían |
| 8 | Estética minimalista | 3 | En móvil la Ruta vacía empuja el composer bajo el pliegue |
| 9 | Recuperación de errores | 3 | Retry lejos del registro fallido en logs largos |
| 10 | Ayuda y documentación | 1 | Sin glosario de tools, `ok · ms` ni rangos |
| **Total** | | **24/40** | **Acceptable (60%)** |

## Design Specificity Verdict

**LLM:** Authored para Teiba, no intercambiable: transecto + bitácora + ruta, hilo copper de 2px con nodos chlorophyll, etiquetas Overpass en mayúsculas, mono tabular, estados icono+texto. Pero viola su propia One Thread Rule: el copper aparece en hilo, icono Wrench, icono Route y diamante operador, diluyendo la firma.

**Detector:** 0 hallazgos en `frontend/src` (exit 0). Sin falsos positivos que filtrar. El detector no vio lo que el juicio sí: enmascaramiento AT, mezcla de turnos en móvil y `openIdx` que no se resetea. Browser visualization omitido (sin automatización de navegador en el harness).

## Overall Impression

Instrumento creíble con firma propia, pero con tres grietas funcionales: el lector de pantalla pierde los datos de la tarjeta, el móvil entierra el composer y la ruta vacía ocupa espacio que no se ha ganado.

## What's Working

- `StatusTag.tsx:17-26`: estado icono+texto en los cuatro estados; nunca solo color.
- `index.css:48-52,98-111`: foco moss 2px global + `prefers-reduced-motion` real.
- `Composer.tsx:44-50` + `ErrorBanner.tsx:46-52`: guard IME `isComposing` y copiar `traceId` con fallback.

## Priority Issues

- **[P0] Tarjeta que enmascara datos para AT** — `SensorCard.tsx:19`: el `aria-label` del botón reemplaza sector, pH, temperatura, batería y antigüedad. Fix: quitar el `aria-label`, dejar el contenido accesible y anteponer "Preguntar por" como `sr-only`. Sugiere: `/impeccable harden`.
- **[P1] Móvil entierra el composer** — `SageView.tsx:122-124`: `FieldLog` + `SignalPath` vacía + composer apilados siempre. Fix: colapsar la Ruta en móvil hasta haber selección; no renderizar el placeholder vacío. Sugiere: `/impeccable layout`.
- **[P1] Live region que re-anuncia todo** — `FieldLog.tsx:22`: `role=log aria-live=polite` envuelve la lista completa. Fix: `aria-live` solo en el `LogEntry` asistente nuevo, contenedor sin live. Sugiere: `/impeccable harden`.
- **[P2] Traza abierta equivocada al cambiar de respuesta** — `SignalPath.tsx:8`: `openIdx` no se resetea con `message`. Fix: `useEffect(()=>setOpenIdx(0),[message?.id])` o `key={message.id}`. Sugiere: `/impeccable polish`.
- **[P2] Pills de estado ocultos en móvil** — `AppShell.tsx:63-67`: mongo/modelo ocultos donde más importan. Fix: un pill compacto siempre visible. Sugiere: `/impeccable layout`.

## Persona Red Flags

- **Alex (power):** `Composer.tsx:60-67` exige puntero; sin `Cmd/Ctrl+Enter`, sin historial, sin reenvío. `SignalNode.tsx:52-64` sin botón Copiar en args/resultado.
- **Sam (accesibilidad):** tarjeta con `aria-label` que borra datos; `SignalNode.tsx:29-30` `truncate` sin `title`, pierde el resumen con zoom 200%.
- **Casey (móvil):** transecto de 5 cards `min-w-[228px]` sin progreso; composer sticky que se confunde con el footer; botón ghost "Actualizar" solo-icono en móvil.

## Minor Observations

- Badge `ok · ms` a 11px: verificar contraste AA real de `success #2f7d4f`.
- Tercer y cuarto copper por respuesta: auditar One Thread Rule.
- Botón Enviar `disabled` mudo: anunciar el mínimo de 3 caracteres.
- `key={tool-index}` colisiona si Sage repite tool; usar índice + traceId.
- `SignalDetail` vuelca JSON crudo sin glosario de rangos.

## Questions to Consider

- Si el cobre es un solo hilo por respuesta, ¿qué tres cobres sobran y cuál se queda?
- Si el operador ya confía en los estados, ¿para qué mostrarle el JSON crudo en vez de la evaluación de rangos?
- En campo con una mano: ¿el 5º sensor visible o un composer siempre a la vista?
