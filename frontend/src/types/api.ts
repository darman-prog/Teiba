// DTOs espejo del contrato HTTP (snake_case). La evaluación de rangos vive en el backend.
export type SensorEstado = 'ok' | 'warning' | 'danger' | 'sin_datos';

export interface UltimaLectura {
  timestamp: string | null;
  humedad: number | null;
  ph: number | null;
  temperatura: number | null;
  bateria: number | null;
  antiguedad_min: number | null;
}

export interface SensorItem {
  id: string;
  tipo: string;
  marca: string | null;
  sector: string | null;
  sector_id: string | null;
  parque: string | null;
  comuna: string | null;
  depende_de: string | null;
  alimentado_por: string | null;
  ultima_lectura: UltimaLectura | null;
  estado: SensorEstado;
}

export interface SensorListResponse {
  items: SensorItem[];
  total: number;
}

export interface HealthResponse {
  status: 'ok' | 'degraded';
  mongo: { ok: boolean; db: string };
  llm: { configurado: boolean; modelo: string };
  version: string;
}

export interface TraceItem {
  tool: string;
  args: Record<string, unknown>;
  ok: boolean;
  ms: number;
  resumen: string;
  resultado: string | null;
}

export interface ConsultaMeta {
  modelo: string;
  pasos: number;
  duracion_ms: number;
  cached: boolean;
  trace_id: string;
}

export interface ConsultaResponse {
  respuesta: string;
  trazas: TraceItem[];
  meta: ConsultaMeta;
}

export interface ParqueResumen {
  codigo: string;
  nombre: string;
  comuna: string | null;
  direccion: string | null;
  area_m2: number | null;
  tipo_parque: string | null;
  estado_general: string | null;
  total_sectores: number;
}

export interface ParqueListResponse {
  items: ParqueResumen[];
  total: number;
}

export interface ParqueSector {
  codigo: string | null;
  nombre: string;
  tipo_suelo: string | null;
  zona_riesgo: string | null;
}

export interface Indicacion {
  nivel: 'info' | 'warning';
  mensaje: string;
}

export interface ParqueDetalle {
  codigo: string;
  nombre: string;
  comuna: string | null;
  direccion: string | null;
  area_m2: number | null;
  tipo_parque: string | null;
  estado_general: string | null;
  sectores: ParqueSector[];
  indicaciones: Indicacion[];
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: unknown;
  traceId?: string;
}
