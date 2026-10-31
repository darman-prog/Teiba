---
name: Teiba Sage
description: Estación de campo que vuelve trazable al agente Sage sobre sensores de parques.
colors:
  primary: "#24513e"
  primary-deep: "#1a3d2f"
  copper: "#a65a3a"
  chlorophyll: "#6fa84a"
  signal: "#d98a1f"
  water: "#2f7f7a"
  mineral: "#f1f4ef"
  surface: "#ffffff"
  ink: "#16201b"
  field-gray: "#5b6b61"
  border: "#d8ded6"
  warn: "#b54708"
  warn-soft: "#fef3ea"
  danger: "#b42318"
  danger-soft: "#feedec"
  success: "#2f7d4f"
  success-soft: "#ecfdf3"
  neutral-soft: "#eef1ec"
typography:
  display:
    fontFamily: "Overpass, Public Sans, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.01em"
  body:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Overpass, Public Sans, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.33
    letterSpacing: "0.08em"
  mono:
    fontFamily: "Spline Sans Mono, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 400
rounded:
  tag: "4px"
  field: "6px"
  card: "8px"
spacing:
  sm: "8px"
  md: "12px"
  lg: "16px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.primary-deep}"
    textColor: "{colors.surface}"
    rounded: "{rounded.field}"
    padding: "8px 16px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "8px 14px"
  input-textarea:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "8px 12px"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.field-gray}"
    typography: "{typography.label}"
    rounded: "{rounded.tag}"
    padding: "2px 8px"
  sensor-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "12px"
  signal-node:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "8px 12px"
---

# Design System: Teiba Sage

## Overview

**Creative North Star: "La Estación de Campo"**

Teiba Sage se comporta como un instrumento de campo calibrado, no como un
chatbot. La estación mide, la bitácora anota, la ruta de la señal prueba.
Cada pantalla responde una sola pregunta del operador: ¿qué pasa en el
parque y cómo lo sabes? La densidad es operativa pero contenida; nada
brilla, nada decora, todo mide.

**Key Characteristics:**
- Instrumento antes que interfaz: etiquetas, monospace tabular y estados LED.
- Un solo hilo de cobre recorre cada respuesta: la traza es la firma.
- Contenido denso, croma mínima: el color solo habla de estado.

## Colors

Verde musgo profundo sobre mineral frío; el cobre marca el único hilo narrativo.

### Primary
- **Moss Station** (#24513e): acciones primarias, focos, marca. Solo sobre surface o blanco.
- **Copper Thread** (#a65a3a): hilo de la ruta, iconos de herramienta, selección. Acento único.

### Secondary
- **Chlorophyll Node** (#6fa84a): nodos vivos de la ruta. Nunca como texto.
- **Signal Amber** (#d98a1f): espera y advertencias ambientales. Nunca como texto.

### Tertiary
- **Station Water** (#2f7f7a): información secundaria y enlaces de datos.

### Neutral
- **Mineral Wash** (#f1f4ef): fondo de página.
- **Surface White** (#ffffff): tarjetas, composer, header.
- **Field Ink** (#16201b): texto principal.
- **Field Gray** (#5b6b61): texto secundario y etiquetas.
- **Fence Line** (#d8ded6): bordes de 1px.
- **Neutral Soft** (#eef1ec): fondos activos y hover silenciosos.

### Named Rules
**The Text-Never Rule.** Chlorophyll y signal jamás visten texto; solo nodos, hilos y puntos de espera. El texto de estado usa warn/danger/success sobre sus soft.
**The One Thread Rule.** El copper aparece una vez por respuesta: el hilo de la ruta. Si todo es cobre, nada es la señal.

## Typography

**Display Font:** Overpass (with Public Sans, system-ui)
**Body Font:** Public Sans (with system-ui)
**Label/Mono Font:** Overpass para etiquetas; Spline Sans Mono para datos

**Character:** Señalización de estación: Overpass rotula instrumentos, Public Sans informa sin fricción, la mono tabula cada cifra.

### Hierarchy
- **Display** (600, 20px/1.2, +0.01em): títulos de vista como “Bitácora de campo”.
- **Headline** (600, 15–17px): marca “Teiba · Sage” y nombres de sección.
- **Title** (600, 14px): botones primarios y nombres de tarjeta.
- **Body** (400, 14px/1.55): respuestas, mensajes, ayudas. Ancho libre en bitácora.
- **Label** (600, 12px, +0.08em, uppercase): etiquetas de instrumento (“PREGUNTA”, “ARGUMENTOS”).

### Named Rules
**The Instrument Label Rule.** Toda etiqueta de campo es Overpass 600, 12px, mayúsculas con tracking. Nada de etiquetas en body ni en itálica.

## Layout

Columna única centrada (`max-w-6xl`) sobre mineral; la estación respira por ritmo, no por aire. Desktop ≥1280: bitácora 7/12 + ruta 5/12 con ruta fija al hacer scroll. Tablet 768–1279: tabs Bitácora/Ruta. Móvil <768: una columna, transecto con scroll-snap horizontal, composer fijo abajo con safe-area.

## Elevation & Depth

Plano por defecto con capas tonales: surface sobre mineral, neutral-soft para activos. Sin sombras de elevación; la profundidad la dan el borde de 1px y el header fijo con blur. El `backdrop-blur` del header es la única excepción admitida.

## Shapes

Esquinas contenidas y funcionales: tags 4px, campos y botones 6px, tarjetas 8px. Bordes de 1px en `border`. Motivo firma: hilo vertical copper de 2px con nodos chlorophyll de 12px en la ruta de la señal.

## Components

### Buttons
- **Shape:** radio contenido (6px), padding 8px 16px, mínimo táctil 44px en móvil.
- **Primary:** fondo moss, texto blanco; hover moss-deep; deshabilitado en border con texto field-gray.
- **Hover / Focus:** solo cambio de tono; foco visible moss de 2px con offset 2px.
- **Secondary / Ghost / Tertiary:** secondary con borde; ghost sin borde para acciones silenciosas; danger invierte a fondo danger en hover.

### Chips
- **Style:** fondo surface, texto field-gray 12px medio, borde 1px, radio 4px.
- **State:** informativos, sin estado seleccionado propio.

### Cards / Containers
- **Corner Style:** tarjeta contenida (8px).
- **Background:** surface sobre mineral.
- **Shadow Strategy:** sin sombras; ver Elevation & Depth.
- **Border:** 1px `border`; hover a moss en tarjetas accionables.
- **Internal Padding:** 12px (md).

### Inputs / Fields
- **Style:** borde 1px, radio 6px, fondo surface con tinte mineral al 40% en el composer.
- **Focus:** borde moss (vía anillo del formulario); sin resplandores.
- **Error / Disabled:** deshabilitado al 60% de opacidad; contador mono 0/500 con `aria-describedby`.

### Navigation
- Station bar fija con marca Teiba, subtítulo y switch de rol; sin pills de estado ni navegación entre secciones. Iconos lucide 1.5px con texto siempre visible.

### SignalPath (firma)
- Hilo copper vertical con nodos: chlorophyll si la tool cumplió, danger si falló.
- Cada nodo es botón `aria-expanded`/`aria-controls` con tool en mono, resumen y `ok · ms`.
- El detalle muestra argumentos y resultado crudo con scroll interno; el JSON es string, no objeto.

### SensorCard
- Ficha de instrumento con número de nodo mono en base 01 sobre el borde, ID en mono 15px, sector a 13px, rejilla pH/temperatura/batería en mono 12px, antigüedad en mono 11px. Botón completo que precarga la pregunta; contenido accesible con `sr-only` + `aria-describedby`, sin `aria-label` enmascarador.

## Do's and Don'ts

### Do:
- **Do** usar un solo acento copper por respuesta: el hilo de la ruta.
- **Do** vestir cada estado con icono + texto, nunca solo color.
- **Do** tabular cada cifra en Spline Sans Mono con `tabular-nums`.
- **Do** anunciar carga, respuesta y error con regiones live.

### Don't:
- **Don't** usar chlorophyll o signal como color de texto.
- **Don't** redondear por encima de 8px ni añadir sombras decorativas.
- **Don't** convertir el composer en un hero ni la bitácora en burbujas de chat genéricas.
- **Don't** exponer la key ni la URI de Mongo en el navegador.
