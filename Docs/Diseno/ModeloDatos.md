# Modelo de Datos — Proyecto Teiba (Bases de Datos II NoSQL)

Este documento especifica el diseño conceptual y lógico de la base de datos para la plataforma **Teiba** (gestión integral de parques urbanos y monitoreo IoT con agente inteligente Sage en Bucaramanga). Cumple los requerimientos de la Entrega 2 y el `DocumentoBase.md` (:52-115, :180-182, :220-253).

---

## 1. Trazabilidad de Entidades contra Requisitos (`DocumentoBase.md:52-115`)

El modelo contempla **8 entidades** (superando el mínimo de 7 exigido por la rúbrica), directamente derivadas de los módulos funcionales del enunciado:

| Entidad | Módulo en `DocumentoBase.md` | Justificación y Responsabilidad en el Dominio |
|---|---|---|
| **`parques`** | Gestión de Parques (`:54-59`) | Entidad raíz del espacio público: nombre, comuna, coordenadas geoespaciales, área y estado general. |
| **`sectores`** | Gestión de Parques y Zonificación (`:58, 92`) | Subdivisión funcional y física de cada parque (e.g. Zona Infantil, Sendero, Cancha Deportiva) para geolocalización de activos y análisis de riesgo. |
| **`dispositivos`** | Tecnologías IoT / Infraestructura (`:194`, Contexto IoT) | Hardware de sensado, telecomunicaciones e iluminación (sensores de suelo, estaciones meteorológicas, luminarias, antenas). Modela la topología de red (`depende_de`). |
| **`lecturas`** | Monitoreo y Telemetría IoT (`:194`, Contexto IoT) | Serie temporal de alta frecuencia con mediciones ambientales (humedad, pH, temperatura, batería) consumida por el agente Sage. |
| **`elementos_inventario`** | Gestión de Inventario (`:60-69`) | Mobiliario urbano e infraestructura física (bancas, juegos infantiles, canchas, luminarias físicas), con cantidad y estado de conservación. |
| **`mantenimientos`** | Gestión de Mantenimiento (`:70-84`) | Órdenes de trabajo preventivas y correctivas programadas y ejecutadas sobre parques o elementos de inventario. |
| **`incidentes`** | Reportes Ciudadanos (`:85-97`) | Reportes de anomalías reportadas por la ciudadanía (seguridad, limpieza, infraestructura, ambiental) con prioridad, estado y evidencia. |
| **`usuarios`** | Gestión de Usuarios y Roles (`:98-106`) | Actores autenticados en el sistema con roles diferenciados: Administrador, Operador de mantenimiento y Ciudadano. |

---

## 2. Modelo Entidad-Relación Conceptual (Notación de Chen)

### 2.1. Checklist Chen Completo (Rúbrica Oficial UNAB)
- [x] **Entidades (Rectángulos):** 8 entidades principales distribuidas en cuadrícula simétrica 3x3 con `Parque` como entidad central.
- [x] **Atributos (Elipses):** 38 elipses de atributos distribuidas en abanicos radiales externos sin cruces de líneas.
- [x] **Relaciones (Rombos):** 9 relaciones binarias conectando estrictamente dos entidades cada una (`Reporta`, `Ejecuta`, `Registra`, `Contiene`, `Aloja`, `Afecta`, `Aplica_A`, `Posee`, `Genera`), con razón global `1:N` junto al rombo.
- [x] **Cardinalidad y Participación (Total vs. Parcial):** Expresadas mediante pares `(mín, máx)` en cada segmento de línea según la guía oficial docente: `(1,1)` para participación total obligatoria y `(0,N)` / `(0,1)` para participación parcial opcional.
- [x] **Llaves Primarias (Atributos Identificadores):** Atributos únicos subrayados con trazo continuo (`_id` en las 7 entidades maestras y `timestamp` como llave temporal en `Lectura`).

### 2.2. Mapa Textual y Topológico de Relaciones Chen

```text
  ┌──────────┐ (0,N)          (1,1) ┌───────────┐          ┌──────────┐
  │ Usuario  │──────[Reporta]───────│ Incidente │          │  Sector  │
  └────┬─────┘        1:N           └─────┬─────┘          └──┬────┬──┘
       │ (0,N)                            │ (1,1)        (1,1)│    │ (0,N)
       │                                  │                   │    │
   [Ejecuta] 1:N                      [Registra] 1:N   [Contiene] [Aloja] 1:N
       │                                  │              1:N  │    │
       │ (1,1)                            │ (0,N)        (0,N)│    │ (1,1)
  ┌────┴──────────┐ (1,1)     (0,N) ┌─────┴─────┐◄────────────┘ ┌──┴──────────┐
  │ Mantenimiento │─────[Afecta]────│  Parque   │               │ Dispositivo │
  └────┬──────────┘       1:N       └─────┬─────┘               └──────┬──────┘
       │ (0,1)                            │ (0,N)                      │ (0,N)
       │                                  │                            │
   [Aplica_A] 1:N                      [Posee] 1:N                 [Genera] 1:N
       │                                  │                            │
       │ (0,N)                      (1,1) │                            │ (1,1)
  ┌────┴───────────────┐                  │                     ┌──────┴──────┐
  │ Elemento_Inventario│◄─────────────────┘                     │   Lectura   │
  └────────────────────┘                                        └─────────────┘
```

### 2.3. Especificación Dibujable de Componentes Chen (Guía de Construcción Gráfica)

Para trasladar este modelo a la herramienta de dibujo (Draw.io, Lucidchart o Visio) requerida por el profesor:

#### 1. Entidad `Parque` (`parques`)
- **Símbolo:** Rectángulo central.
- **Atributos (Elipses conectadas):**
  - <u>`_id`</u> (Identificador único, clave primaria subrayada).
  - `nombre` (Cadena, e.g. "Parque San Pío").
  - `ubicacion` (Ubicación física y geoespacial del parque).
  - `area_m2` (Numérico decimal).
  - `tipo_parque` (Cadena: recreativo, ecológico, infantil, deportivo).
  - `estado_general` (Cadena: bueno, regular, deteriorado).

#### 2. Entidad `Sector` (`sectores`)
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`_id`</u> (Clave primaria subrayada).
  - `nombre` (Cadena, e.g. "Zona de Juegos Infantiles", "Sendero Norte").
  - `tipo_suelo` (Cadena, e.g. "Césped natural", "Pavimento blando", "Tierra arcillosa").
  - `zona_riesgo` (Cadena: alta, media, baja, ninguna).
- **Relación con `Parque` (`Contiene` — `1:N`):**
  - Participación en `Parque`: `(0,N)` (parcial).
  - Participación en `Sector`: `(1,1)` (total: un sector no puede existir sin su parque).

#### 3. Entidad `Dispositivo` (`dispositivos`)
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`_id`</u> (Clave primaria subrayada, e.g. "SS-01", "GW-01").
  - `tipo` (Cadena: calidad_suelo, estacion_meteorologica, luminaria_inteligente, antena_enlace).
  - `marca` (Cadena).
  - `alimentado_por` (Cadena, e.g. "Panel_Solar_S1", "Red_Electrica_T1").
- **Relación con `Sector` (`Aloja` — `1:N`):**
  - Participación en `Sector`: `(0,N)` (parcial) y en `Dispositivo`: `(1,1)` (total).
  - *Nota de implementación MongoDB:* El atributo `depende_de` se almacena como metadato documental interno dentro de la colección `dispositivos` sin requerir relación recursiva en el diagrama conceptual.

#### 4. Entidad `Lectura` (`lecturas` — Serie de Tiempo IoT)
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`timestamp`</u> (Instante exacto `Date/ISODate` de la medición, llave primaria subrayada de la serie de tiempo).
  - `humedad` (Numérico).
  - `ph` (Numérico).
  - `temperatura` (Numérico).
  - `bateria` (Numérico).
- **Relación con `Dispositivo` (`Genera` — `1:N`):**
  - Participación en `Dispositivo`: `(0,N)` (parcial) y en `Lectura`: `(1,1)` (total: toda lectura proviene obligatoriamente de un sensor).

#### 5. Entidad `elementos_inventario`
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`_id`</u> (Clave primaria).
  - `tipo_elemento` (Cadena: banca, luminaria, columpio, cancha, sendero).
  - `cantidad` (Entero positivo).
  - `estado` (Cadena: bueno, danado, en_mantenimiento).
- **Relación con `parques` (`Posee`):**
  - Rombo `Posee`.
  - Participación: `parques` (parcial, 1) a `elementos_inventario` (total, N: doble línea).

#### 6. Entidad `mantenimientos`
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`_id`</u> (Clave primaria).
  - `tipo` (Cadena: preventivo, correctivo).
  - `descripcion` (Texto).
  - `fecha_programada` (Fecha).
  - `fecha_ejecucion` (Fecha opcional/nula si pendiente).
  - `estado` (Cadena: pendiente, en_proceso, finalizado).
  - `costo_estimado` (Moneda / Numérico).
- **Relación con `parques` (`Afecta`):**
  - Rombo `Afecta`. Participación total hacia `mantenimientos` (doble línea), 1:N.
- **Relación con `elementos_inventario` (`Aplica_A`):**
  - Rombo `Aplica_A`. Participación parcial en ambos extremos (0..1 elemento por mantenimiento, 0..N mantenimientos por elemento).
- **Relación con `usuarios` (`Ejecuta` / `Asignado_A`):**
  - Rombo `Ejecuta`. Participación total en `mantenimientos` (doble línea: toda orden tiene un responsable), 1:N desde `usuarios`.

#### 7. Entidad `incidentes`
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`_id`</u> (Clave primaria).
  - `tipo` (Cadena: seguridad, limpieza, infraestructura, ambiental).
  - `descripcion` (Texto).
  - `fecha_hora` (Fecha y hora).
  - `estado` (Cadena: reportado, en_revision, en_proceso, resuelto).
  - `prioridad` (Cadena: alta, media, baja).
- **Relación con `parques` (`Registra`):**
  - Rombo `Registra`. Participación total en `incidentes` (doble línea), 1:N desde `parques`.
- **Relación con `usuarios` (`Reporta`):**
  - Rombo `Reporta`. Participación total en `incidentes` (doble línea: no anónimo), 1:N desde `usuarios`.

#### 8. Entidad `usuarios`
- **Símbolo:** Rectángulo.
- **Atributos (Elipses):**
  - <u>`_id`</u> (Clave primaria).
  - `nombre` (Cadena).
  - `correo` (Cadena, clave alternativa / unique).
  - `telefono` (Cadena).
  - `rol` (Cadena: administrador, operador_mantenimiento, ciudadano).
  - `fecha_registro` (Fecha).

---

## 3. Diseño Lógico de Documentos en MongoDB

Conforme a la rúbrica oficial de MongoDB de `DocumentoBase.md:240-253`:
1. Tabla de entidades y atributos.
2. Tabla de descripción de relaciones.
3. Modelo de colecciones (JSON Schema y estructuras BSON).

### 3.1. Tabla de Entidades y Atributos

| Entidad (Colección) | Campo / Atributo | Tipo de Dato BSON | Tamaño / Formato | Descripción del Campo |
|---|---|---|---|---|
| **`parques`** | `_id` | ObjectId | 12 bytes | Clave primaria autogenerada única |
| | `codigo` | String | 10 caracteres | Código nemotécnico (e.g. "PRQ-001") |
| | `nombre` | String | 80 caracteres | Nombre oficial del parque |
| | `ubicacion` | Object (Subdocumento) | — | Objeto con dirección, comuna y GeoJSON |
| | `ubicacion.direccion` | String | 120 caracteres | Dirección física catastral |
| | `ubicacion.comuna` | String | 40 caracteres | Nombre/número de comuna |
| | `ubicacion.coordenadas` | GeoJSON Point | Array [long, lat] | Coordenadas WGS84 para índice 2dsphere |
| | `area_m2` | Double | 8 bytes | Área total en metros cuadrados |
| | `tipo_parque` | String | 25 caracteres | recreativo, ecológico, infantil, deportivo |
| | `estado_general` | String | 20 caracteres | bueno, regular, deteriorado |
| **`sectores`** | `_id` | ObjectId | 12 bytes | Clave primaria |
| | `codigo` | String | 10 caracteres | Código del sector (e.g. "SEC-001") |
| | `parque_id` | ObjectId | 12 bytes | Referencia al parque contenedor |
| | `nombre` | String | 60 caracteres | Nombre descriptivo del sector |
| | `tipo_suelo` | String | 30 caracteres | césped natural, pavimento blando, tierra arcillosa |
| | `zona_riesgo` | String | 15 caracteres | alta, media, baja, ninguna |
| **`dispositivos`** | `_id` | String | 15 caracteres | Identificador técnico de hardware (e.g. "SS-01", "GW-01") |
| | `tipo` | String | 30 caracteres | calidad_suelo, estacion_meteorologica, luminaria_inteligente, antena_enlace |
| | `marca` | String | 40 caracteres | Marca del fabricante |
| | `fecha_instalacion` | Date (ISODate) | 8 bytes | Fecha de puesta en marcha |
| | `sector_id` | ObjectId | 12 bytes | Referencia al sector físico |
| | `parque_id` | ObjectId | 12 bytes | Referencia desnormalizada para consultas rápidas |
| | `depende_de` | String (Nullable) | 15 caracteres | ID del nodo repetidor del que depende |
| | `alimentado_por` | String | 50 caracteres | Fuente de energía |
| **`lecturas`** | `timestamp` | Date (ISODate) | 8 bytes | Marca temporal de la muestra (timeField) |
| | `meta` | Object | — | Metadatos de agrupamiento (metaField) |
| | `meta.sensor_id` | String | 15 caracteres | ID del sensor generador |
| | `meta.tipo` | String | 30 caracteres | Tipo de sensor |
| | `humedad` | Double | 8 bytes | Porcentaje de humedad (0 - 100 %) |
| | `ph` | Double | 8 bytes | Potencial de hidrógeno (0.0 - 14.0) |
| | `temperatura` | Double | 8 bytes | Temperatura en grados Celsius (°C) |
| | `bateria` | Int32 | 4 bytes | Nivel de batería (0 - 100 %) |
| **`elementos_inventario`** | `_id` | ObjectId | 12 bytes | Clave primaria |
| | `parque_id` | ObjectId | 12 bytes | Referencia al parque |
| | `sector_id` | ObjectId (Nullable) | 12 bytes | Referencia opcional al sector |
| | `tipo_elemento` | String | 40 caracteres | banca, luminaria, columpio, cancha_multiple, sendero |
| | `cantidad` | Int32 | 4 bytes | Cantidad física inventariada (>= 1) |
| | `estado` | String | 20 caracteres | bueno, danado, en_mantenimiento |
| **`mantenimientos`** | `_id` | ObjectId | 12 bytes | Clave primaria |
| | `tipo` | String | 20 caracteres | preventivo, correctivo |
| | `descripcion` | String | 250 caracteres | Detalle técnico del trabajo |
| | `fecha_programada` | Date (ISODate) | 8 bytes | Fecha planeada de ejecución |
| | `fecha_ejecucion` | Date (Nullable) | 8 bytes | Fecha efectiva (null si pendiente) |
| | `estado` | String | 20 caracteres | pendiente, en_proceso, finalizado |
| | `parque_id` | ObjectId | 12 bytes | Referencia al parque intervenido |
| | `elemento_id` | ObjectId (Nullable) | 12 bytes | Referencia al elemento de mobiliario intervenido |
| | `responsable_id` | ObjectId | 12 bytes | Referencia al usuario operador asignado |
| | `costo_estimado` | Double | 8 bytes | Presupuesto en pesos colombianos (COP) |
| **`incidentes`** | `_id` | ObjectId | 12 bytes | Clave primaria |
| | `tipo` | String | 25 caracteres | seguridad, limpieza, infraestructura, ambiental |
| | `descripcion` | String | 300 caracteres | Relato ciudadano de la situación |
| | `fecha_hora` | Date (ISODate) | 8 bytes | Momento exacto del reporte |
| | `parque_id` | ObjectId | 12 bytes | Referencia al parque afectado |
| | `reportado_por_id` | ObjectId | 12 bytes | Referencia al usuario ciudadano |
| | `estado` | String | 20 caracteres | reportado, en_revision, en_proceso, resuelto |
| | `prioridad` | String | 15 caracteres | alta, media, baja |
| | `evidencias` | Array de Objetos | Embebido 1:P | Lista de URLs y comentarios de fotos |
| **`usuarios`** | `_id` | ObjectId | 12 bytes | Clave primaria |
| | `nombre` | String | 80 caracteres | Nombre y apellidos del usuario |
| | `correo` | String | 100 caracteres | Correo electrónico institucional/personal |
| | `telefono` | String | 20 caracteres | Número telefónico de contacto |
| | `rol` | String | 25 caracteres | administrador, operador_mantenimiento, ciudadano |
| | `fecha_registro` | Date (ISODate) | 8 bytes | Fecha de alta en el sistema |

---

### 3.2. Tabla de Descripción de Relaciones

| Entidad Origen | Entidad Destino | Cardinalidad | Estrategia en MongoDB | Justificación Técnica de Persistencia |
|---|---|---|---|---|
| `parques` | `sectores` | 1:N | Referenciada (`parque_id`) | Mantiene acotado el tamaño del documento de parque y permite gestionar sectores independientemente. |
| `sectores` | `dispositivos` | 1:N | Referenciada (`sector_id`, `parque_id`) | Desacopla la gestión del hardware de la subdivisión del terreno. Incluye `parque_id` desnormalizado para acelerar filtros. |
| `dispositivos` | `dispositivos` | 1:N (recursiva) | Referenciada (`depende_de`) | Representa la topología de red sin nesting indefinido. Evita bucles de embedding. |
| `dispositivos` | `lecturas` | 1:N | Colección Time-Series (`meta.sensor_id`) | **Crucial:** Embeber telemetría en el dispositivo rompería el límite de 16MB (anti-patrón unbounded array). La colección time-series comprime columnarmente. |
| `parques` | `elementos_inventario` | 1:N | Referenciada (`parque_id`) | Los parques contienen cientos de elementos; referenciar evita saturar lecturas/escrituras en el documento del parque. |
| `elementos_inventario`| `mantenimientos` | 0..1:N | Referenciada (`elemento_id` opcional) | Muchas órdenes atienden áreas generales sin un elemento específico; referenciar permite valores nulos limpios. |
| `parques` | `mantenimientos` | 1:N | Referenciada (`parque_id`) | Permite consultar el historial de trabajo por parque mediante `$lookup` sin duplicar información. |
| `usuarios` | `mantenimientos` | 1:N | Referenciada (`responsable_id`) | Asigna la responsabilidad laboral al operador sin anidar los mantenimientos en el perfil del usuario. |
| `parques` | `incidentes` | 1:N | Referenciada (`parque_id`) | El flujo ciudadano genera miles de quejas que deben agregarse con `$group` y `$lookup` sin inflar el parque. |
| `usuarios` | `incidentes` | 1:N | Referenciada (`reportado_por_id`) | Garantiza la trazabilidad del ciudadano reportante cumpliendo con el RF :87. |

---

### 3.3. Modelo de Colecciones (Estructura de Documentos JSON)

#### Colección `parques`
```json
{
  "_id": { "$oid": "671150000000000000000001" },
  "codigo": "PRQ-001",
  "nombre": "Parque San Pío",
  "ubicacion": {
    "direccion": "Carrera 33 con Calle 45",
    "comuna": "Comuna 12 - Cabecera del Llano",
    "coordenadas": {
      "type": "Point",
      "coordinates": [-73.1114, 7.1192]
    }
  },
  "area_m2": 15400.0,
  "tipo_parque": "recreativo",
  "estado_general": "bueno"
}
```

#### Colección `sectores`
```json
{
  "_id": { "$oid": "671151000000000000000001" },
  "codigo": "SEC-001",
  "parque_id": { "$oid": "671150000000000000000001" },
  "nombre": "Sector Norte - Jardines de la Escultura",
  "tipo_suelo": "césped natural",
  "zona_riesgo": "baja"
}
```

#### Colección `dispositivos`
```json
{
  "_id": "SS-01",
  "tipo": "calidad_suelo",
  "marca": "SoilPro-Sense",
  "fecha_instalacion": { "$date": "2026-02-15T08:00:00Z" },
  "sector_id": { "$oid": "671151000000000000000001" },
  "parque_id": { "$oid": "671150000000000000000001" },
  "depende_de": "ANT-01",
  "alimentado_por": "Panel_Solar_PS1"
}
```

#### Colección `lecturas` (Time-Series)
```json
{
  "timestamp": { "$date": "2026-10-17T18:00:00Z" },
  "meta": {
    "sensor_id": "SS-01",
    "tipo": "calidad_suelo"
  },
  "humedad": 38.5,
  "ph": 6.45,
  "temperatura": 21.2,
  "bateria": 94
}
```

#### Colección `elementos_inventario`
```json
{
  "_id": { "$oid": "671152000000000000000001" },
  "parque_id": { "$oid": "671150000000000000000001" },
  "sector_id": { "$oid": "671151000000000000000001" },
  "tipo_elemento": "juego_infantil",
  "cantidad": 3,
  "estado": "bueno"
}
```

#### Colección `mantenimientos`
```json
{
  "_id": { "$oid": "671153000000000000000001" },
  "tipo": "preventivo",
  "descripcion": "Poda fitosanitaria y calibración de aspersores de riego",
  "fecha_programada": { "$date": "2026-10-20T07:00:00Z" },
  "fecha_ejecucion": null,
  "estado": "pendiente",
  "parque_id": { "$oid": "671150000000000000000001" },
  "elemento_id": null,
  "responsable_id": { "$oid": "671154000000000000000002" },
  "costo_estimado": 350000.0
}
```

#### Colección `incidentes`
```json
{
  "_id": { "$oid": "671155000000000000000001" },
  "tipo": "infraestructura",
  "descripcion": "Luminaria solar intermitente en el sendero peatonal",
  "fecha_hora": { "$date": "2026-10-16T19:30:00Z" },
  "parque_id": { "$oid": "671150000000000000000001" },
  "reportado_por_id": { "$oid": "671154000000000000000003" },
  "estado": "en_revision",
  "prioridad": "media",
  "evidencias": [
    {
      "url": "https://teiba.bucaramanga.gov.co/evidencias/inc-001-a.jpg",
      "comentario": "Foto de la luminaria apagada de noche"
    }
  ]
}
```

#### Colección `usuarios`
```json
{
  "_id": { "$oid": "671154000000000000000001" },
  "nombre": "Carlos Gómez Parra",
  "correo": "cgomez@bucaramanga.gov.co",
  "telefono": "+57 315 7894512",
  "rol": "administrador",
  "fecha_registro": { "$date": "2026-01-10T08:00:00Z" }
}
```
