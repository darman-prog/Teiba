# ADR 001: Selección de MongoDB como Base de Datos Única para Teiba

## Contexto
El proyecto de curso de Bases de Datos II (Ingeniería de Sistemas, UNAB) requiere la concepción, modelado e implantación de un sistema integral de gestión para los parques urbanos del área metropolitana de Bucaramanga (`Docs/DocumentoBase.md`), incorporando además un agente inteligente autónomo (**Sage**) para el monitoreo de telemetría IoT.

La rúbrica académica exige:
1. Mínimo 7 entidades y al menos 10 registros por entidad.
2. 5 consultas de negocio relevantes que involucren un mínimo de 2 colecciones cada una.
3. Modelo Entidad-Relación (notación Chen) y Modelo de Colecciones Documentales o de Grafos.

Inicialmente se exploró una arquitectura políglota combinando MongoDB (para telemetría de series de tiempo) y Neo4j (para la topología de red y relaciones espaciales mediante GraphRAG). Sin embargo, mantener dos motores de bases de datos para un MVP académico introduce una sobrecarga considerable: doble infraestructura, necesidad de sincronización de llaves foráneas entre grafos y documentos, dispersión de scripts de entrega y divergencia frente a la rúbrica del curso, que califica una implementación enfocada y consistente.

## Decisión
Se decide adoptar **MongoDB como motor de base de datos único** para todo el alcance del proyecto **Teiba**, gestionando las 8 entidades del sistema en una única base de datos (`teiba_db`):
- **Telemetría IoT:** Almacenada en la colección de series de tiempo nativa `lecturas` (`timeseries: { timeField: "timestamp", metaField: "meta", granularity: "minutes" }`).
- **Contexto Operativo y Entidades Maestras:** Almacenadas en colecciones estándar documentales referenciadas: `parques`, `sectores`, `dispositivos`, `elementos_inventario`, `mantenimientos`, `incidentes` y `usuarios`.
- **Agente IA (Sage):** Implementará Recuperación Aumentada por Generación basada en herramientas (*Tool-Calling RAG* con la API de OpenCode Go), interactuando con MongoDB mediante funciones específicas de consulta (`list_sensors`, `get_sensor_history`, `get_device_context`).

## Consecuencias
### Positivas
- **Simplicidad de despliegue e infraestructura:** Un único servicio MongoDB (vía Docker `mongo:8` o local) satisface tanto la ingesta masiva de lecturas como los datos maestros.
- **Cumplimiento riguroso de la rúbrica:** Las 8 colecciones superan el mínimo de 7 entidades, centralizando scripts homogéneos de creación (`01_crear_objetos.js`), carga de datos (`02_cargar_datos.js`) y consultas (`03_consultas.js`).
- **Consultas relacionales potentes:** El Aggregation Pipeline de MongoDB (`$lookup`, `$match`, `$unwind`, `$group`) resuelve eficazmente cruces entre colecciones sin requerir un motor de grafos externo para jerarquías de baja profundidad.
- **Consistencia operativa para el agente:** El agente consulta metadatos estáticos y telemetría histórica bajo un mismo cliente y formato BSON/JSON.

### Negativas
- Análisis de impacto en grafos de muy alta profundidad (e.g. cascada de fallas eléctricas con >5 niveles jerárquicos) requiere etapas `$graphLookup` en lugar del acceso nativo *index-free adjacency* de bases de grafos.

### Mitigaciones
- La topología de parques urbanos tiene una profundidad jerárquica acotada (Parque -> Sector -> Dispositivo / Elemento de Inventario). Esta estructura se modela de forma eficiente y limpia mediante referencias directas e índices B-Tree en MongoDB, dejando abierta la migración a Neo4j como trabajo futuro si la escala metropolitana lo demanda.

## Alternativas descartadas
- **Neo4j como base de datos única:** Descartada porque Neo4j no está optimizado para almacenar flujos continuos de alta frecuencia de telemetría IoT (series temporales), lo que causaría sobrecarga en los nodos del grafo.
- **Arquitectura dual políglota (MongoDB + Neo4j):** Descartada para la fase de entrega del curso por riesgo de inconsistencia, doble configuración de scripts y complejidad innecesaria para un MVP académico con datos sintéticos.
- **Grafo simulado en archivos JSON:** Descartada por carecer de rigor técnico, violar los estándares de persistencia y no aportar valor arquitectónico real.
