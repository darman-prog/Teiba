import type {
  ConsultaResponse,
  HealthResponse,
  ParqueDetalle,
  ParqueListResponse,
  SensorListResponse,
} from '../types/api';

// Fixtures idénticas al contrato para VITE_USE_MOCKS=true y tests.
const NOW = '2026-10-24T18:00:00Z';

export const FIXTURE_HEALTH: HealthResponse = {
  status: 'ok',
  mongo: { ok: true, db: 'teiba_db' },
  llm: { configurado: true, modelo: 'deepseek-v4.1-flash' },
  version: '0.1.0',
};

export const FIXTURE_SENSORS: SensorListResponse = {
  total: 5,
  items: [
    {
      id: 'SS-01',
      tipo: 'calidad_suelo',
      marca: 'SoilPro-Sense LoRa',
      sector: 'Sector Norte - Jardines de la Escultura de Botero',
      sector_id: '671151000000000000000001',
      parque: 'Parque San Pío',
      comuna: 'Comuna 12 - Cabecera del Llano',
      depende_de: 'ANT-01',
      alimentado_por: 'Panel_Solar_PS1',
      ultima_lectura: { timestamp: NOW, humedad: 38.0, ph: 5.4, temperatura: 19.0, bateria: 95, antiguedad_min: 0 },
      estado: 'danger',
    },
    {
      id: 'SS-02',
      tipo: 'calidad_suelo',
      marca: 'SoilPro-Sense LoRa',
      sector: 'Sector Sur - Plazoleta',
      sector_id: '671151000000000000000002',
      parque: 'Parque San Pío',
      comuna: 'Comuna 12 - Cabecera del Llano',
      depende_de: 'ANT-01',
      alimentado_por: 'Panel_Solar_PS1',
      ultima_lectura: { timestamp: '2026-10-24T11:00:00Z', humedad: 40.0, ph: 6.5, temperatura: 19.7, bateria: 88, antiguedad_min: 420 },
      estado: 'warning',
    },
    {
      id: 'SS-03',
      tipo: 'calidad_suelo',
      marca: 'SoilPro-Sense LoRa',
      sector: 'Sector Bosque',
      sector_id: '671151000000000000000003',
      parque: 'Parque San Pío',
      comuna: 'Comuna 12 - Cabecera del Llano',
      depende_de: 'ANT-02',
      alimentado_por: 'Panel_Solar_PS2',
      ultima_lectura: { timestamp: NOW, humedad: 42.0, ph: 6.6, temperatura: 20.4, bateria: 15, antiguedad_min: 2 },
      estado: 'danger',
    },
    {
      id: 'SS-04',
      tipo: 'calidad_suelo',
      marca: 'SoilPro-Sense LoRa',
      sector: 'Sector Occidental',
      sector_id: '671151000000000000000004',
      parque: 'Parque San Pío',
      comuna: 'Comuna 12 - Cabecera del Llano',
      depende_de: 'ANT-02',
      alimentado_por: 'Panel_Solar_PS2',
      ultima_lectura: { timestamp: NOW, humedad: 44.0, ph: 6.5, temperatura: 21.1, bateria: 86, antiguedad_min: 1 },
      estado: 'ok',
    },
    {
      id: 'SS-05',
      tipo: 'calidad_suelo',
      marca: 'SoilPro-Sense LoRa',
      sector: 'Sendero de la Quebrada',
      sector_id: '671151000000000000000005',
      parque: 'Parque San Pío',
      comuna: 'Comuna 12 - Cabecera del Llano',
      depende_de: 'ANT-02',
      alimentado_por: 'Panel_Solar_PS2',
      ultima_lectura: { timestamp: NOW, humedad: 46.0, ph: 6.5, temperatura: 21.8, bateria: 83, antiguedad_min: 1 },
      estado: 'ok',
    },
  ],
};

export const FIXTURE_SIN_DATOS_SENSORS: SensorListResponse = {
  total: 1,
  items: [
    {
      id: 'MET-01',
      tipo: 'estacion_meteo',
      marca: 'AtmoField LoRa',
      sector: 'Sector Norte - Jardines de la Escultura de Botero',
      sector_id: '671151000000000000000001',
      parque: 'Parque San Pío',
      comuna: 'Comuna 12 - Cabecera del Llano',
      depende_de: 'ANT-01',
      alimentado_por: 'Panel_Solar_PS1',
      ultima_lectura: null,
      estado: 'sin_datos',
    },
  ],
};

export const FIXTURE_CONSULTA: ConsultaResponse = {
  respuesta:
    'El sensor SS-01, en el Sector Norte del Parque San Pío, reporta humedad de 38.0 %, pH de 5.4 y temperatura de 19.0 °C. El pH está por debajo del rango normal (6.0–7.5).',
  trazas: [
    {
      tool: 'list_sensors',
      args: { tipo: 'calidad_suelo', sector: 'Sector Norte' },
      ok: true,
      ms: 8,
      resumen: '1 dispositivo: SS-01',
      resultado: '{"estado": "ok", "total": 1, "items": ["SS-01"]}',
    },
    {
      tool: 'get_sensor_history',
      args: { sensor_id: 'SS-01', horas: 6 },
      ok: true,
      ms: 21,
      resumen: '49 lecturas; pH fuera de rango',
      resultado: '{"sensor_id": "SS-01", "lecturas": 49, "evaluacion": "ph_bajo"}',
    },
    {
      tool: 'get_device_context',
      args: { device_id: 'SS-01' },
      ok: true,
      ms: 12,
      resumen: 'Sector Norte / ANT-01',
      resultado: '{"device_id": "SS-01", "sector": "Sector Norte", "antena": "ANT-01"}',
    },
  ],
  meta: { modelo: 'deepseek-v4.1-flash', pasos: 4, duracion_ms: 4200, cached: false, trace_id: 'demo-trace-001' },
};

const COMUNAS = ['Comuna 12 - Cabecera del Llano', 'Comuna 3 - San Francisco', 'Comuna 7 - La Ciudadela'];
const TIPOS = ['Metropolitano', 'Zonal', 'Barrial'];
const ESTADOS = ['Bueno', 'Regular', 'En recuperación'];

export const FIXTURE_PARQUES: ParqueListResponse = {
  total: 10,
  items: Array.from({ length: 10 }, (_, i) => {
    const n = i + 1;
    return {
      codigo: `PQ-${String(n).padStart(2, '0')}`,
      nombre: i === 0 ? 'Parque San Pío' : `Parque Demo ${n}`,
      comuna: COMUNAS[i % COMUNAS.length]!,
      direccion: `Calle ${10 + n} #${20 + n}-0${n}`,
      area_m2: 8000 + n * 1500,
      tipo_parque: TIPOS[i % TIPOS.length]!,
      estado_general: ESTADOS[i % ESTADOS.length]!,
      total_sectores: 2 + (i % 3),
    };
  }),
};

export function fixtureParqueDetalle(codigo: string): ParqueDetalle {
  const base = FIXTURE_PARQUES.items.find((p) => p.codigo === codigo) ?? FIXTURE_PARQUES.items[0]!;
  return {
    codigo: base.codigo,
    nombre: base.nombre,
    comuna: base.comuna,
    direccion: base.direccion,
    area_m2: base.area_m2,
    tipo_parque: base.tipo_parque,
    estado_general: base.estado_general,
    sectores: [
      { codigo: 'SEC-001', nombre: 'Sector Norte - Jardines', tipo_suelo: 'Franco', zona_riesgo: 'Baja' },
      { codigo: 'SEC-002', nombre: 'Sector Sur - Plazoleta', tipo_suelo: 'Arcilloso', zona_riesgo: 'Media' },
    ],
    indicaciones: [
      { nivel: 'info', mensaje: 'Riego programado los martes y viernes en el Sector Norte.' },
      { nivel: 'warning', mensaje: 'El Sector Sur presenta compactación; evitar tránsito pesado.' },
    ],
  };
}
