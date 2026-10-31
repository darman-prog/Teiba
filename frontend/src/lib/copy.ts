// Textos de la estación y del libro; el backend es dueño de los datos.
export const SUGERENCIAS_SAGE = [
  '¿Cómo está el suelo del Sector Norte?',
  '¿Qué sensores dependen de ANT-01?',
  '¿Hay algún sensor con batería baja?',
] as const;

export const COPY = {
  skip: 'Saltar al contenido principal',
  nuevaConsulta: 'Nueva consulta',
  verTrazas: (n: number) => `Ver ${n} ${n === 1 ? 'traza' : 'trazas'}`,
  composerLabel: 'Pregunta a Sage',
  composerHint: 'Enter envía · Shift+Enter salta de línea · mínimo 3 caracteres',
  emptyTitle: 'Bitácora lista — aún sin registros',
  emptyBody:
    'Pregunta por un sensor, una antena o una batería. Sage consulta la base y deja la ruta de señales a la derecha.',
  loadingTitle: 'Sage está consultando la base de datos…',
  loadingBody: 'Recuperando lecturas y contexto. Puede tardar hasta un minuto.',
  errorRetry: 'Reintentar',
  errorDiscard: 'Descartar',
  errorCopy: 'Copiar traceId',
  errorCopied: 'Copiado',
} as const;

// Mensaje humano por código de error del contrato.
export function mensajePorCodigo(code: string): string {
  switch (code) {
    case 'db_unavailable':
      return 'La base de datos no está disponible. Revisa Mongo y reintenta.';
    case 'llm_unavailable':
      return 'Sage no pudo contactar al modelo. Reintenta en unos segundos.';
    case 'llm_not_configured':
      return 'El modelo no está configurado en el servidor. Avisá al equipo de backend.';
    case 'timeout':
      return 'La consulta superó el tiempo máximo. Simplifica la pregunta.';
    case 'rate_limited':
      return 'Límite de consultas por minuto. Espera unos segundos y reintenta.';
    case 'invalid_request':
      return 'La pregunta debe tener entre 3 y 500 caracteres.';
    case 'not_found':
      return 'No se encontró el recurso pedido.';
    case 'network':
      return 'Sin conexión con la API. Verifica que el backend esté en marcha.';
    default:
      return 'Ocurrió un error inesperado.';
  }
}
