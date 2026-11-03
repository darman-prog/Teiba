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

// --- Autenticación y sesión ---
export type AuthRole = 'admin' | 'operator' | 'user';
export type DomainRole = 'administrador' | 'operador_mantenimiento' | 'ciudadano';

export interface AuthUser {
  correo: string;
  rol: AuthRole;
}

export interface PerfilUsuario {
  id: string;
  nombre: string;
  correo: string;
  rol: DomainRole;
}

export interface SessionResponse {
  usuario: AuthUser;
  perfil: PerfilUsuario | null;
  expira_en: string;
}

// --- Mantenimientos, incidentes e inventario ---
export type MaintenanceStatus = 'pendiente' | 'en_proceso' | 'finalizado';
export type MaintenancePriority = 'alta' | 'media' | 'baja';
export type IncidentStatus = 'reportado' | 'en_revision' | 'en_proceso' | 'resuelto';

export interface MaintenanceParque {
  id: string;
  codigo: string | null;
  nombre: string;
}

export interface MaintenanceResponsable {
  id: string;
  nombre: string;
  rol: string | null;
}

export interface MaintenanceIncidente {
  id: string;
  tipo: string | null;
  descripcion: string | null;
  prioridad: string | null;
  estado: IncidentStatus | null;
}

export interface MaintenanceElemento {
  id: string;
  tipo_elemento: string | null;
  cantidad: number | null;
  estado: string | null;
}

export interface MaintenanceItem {
  id: string;
  tipo: 'preventivo' | 'correctivo';
  descripcion: string;
  prioridad: MaintenancePriority;
  estado: MaintenanceStatus;
  fecha_programada: string | null;
  fecha_ejecucion: string | null;
  fecha_reapertura: string | null;
  nota_cierre: string | null;
  nota_reapertura: string | null;
  costo_estimado: number | null;
  vencida: boolean;
  parque: MaintenanceParque | null;
  responsable: MaintenanceResponsable | null;
  incidente: MaintenanceIncidente | null;
  elemento: MaintenanceElemento | null;
}

export interface MaintenanceListResponse {
  items: MaintenanceItem[];
  total: number;
}

export interface MaintenanceCreateBody {
  tipo: 'preventivo' | 'correctivo';
  descripcion: string;
  fecha_programada: string;
  prioridad: MaintenancePriority;
  parque_codigo: string;
  responsable_id: string;
  elemento_id?: string | null;
  incidente_id?: string | null;
  costo_estimado?: number | null;
}

export interface MaintenanceEstadoBody {
  estado: 'en_proceso' | 'finalizado';
  nota?: string | null;
}

export interface OperadorItem {
  id: string;
  nombre: string;
}

export interface OperadorListResponse {
  items: OperadorItem[];
  total: number;
}

export interface IncidenteItem {
  id: string;
  tipo: string | null;
  descripcion: string | null;
  fecha_hora: string | null;
  estado: IncidentStatus;
  prioridad: string | null;
  parque: MaintenanceParque | null;
  reportado_por: { id: string; nombre: string } | null;
}

export interface IncidenteListResponse {
  items: IncidenteItem[];
  total: number;
}

export interface ElementoItem {
  id: string;
  tipo_elemento: string | null;
  cantidad: number | null;
  estado: string | null;
  sector: { id: string; codigo: string | null; nombre: string | null } | null;
}

export interface ElementoListResponse {
  items: ElementoItem[];
  total: number;
}
