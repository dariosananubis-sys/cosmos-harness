// docker-job-log-markers.js — parsers puros de la salida (no confiable) de un contenedor de
// job: demux de frames Docker + un protocolo mínimo de marcadores `::PREFIX::{json}` para que
// un contenedor efímero reporte metadatos y progreso por stdout, sin necesitar una API/socket
// adicional. Dep-free (sin dockerode) → testeable sin Docker real. La parte de streaming en
// vivo (leer el log mientras el contenedor corre) vive en el orquestador; aquí solo el parseo
// de cada línea/buffer, que es lo que de verdad conviene tener cubierto por tests.

// Prefijos por defecto del protocolo; el caller puede usar los suyos (parsePrefixedJsonArray
// y parseStepLine no dependen de estas constantes en concreto).
export const JOB_META_PREFIX = '::JOB_META::';
export const JOB_STEP_PREFIX = '::JOB_STEP::';

/**
 * Desmultiplexa el stream de logs de Docker (8 bytes de header por frame: 1 byte stream type +
 * 3 reservados + 4 de tamaño big-endian).
 * @param {Buffer} raw
 * @param {number} [tail=100] nº de líneas finales a conservar
 * @returns {string} texto plano (últimas `tail` líneas)
 */
export function demuxLogs(raw, tail = 100) {
  const lines = [];
  let offset = 0;
  while (offset + 8 <= raw.length) {
    const size = raw.readUInt32BE(offset + 4);
    offset += 8;
    if (size > 0 && offset + size <= raw.length) {
      lines.push(raw.slice(offset, offset + size).toString('utf8'));
      offset += size;
    } else {
      // Frame truncado (buffer cortado): no descartar el resto en silencio.
      if (offset < raw.length) console.warn('[docker-job-log-markers] demuxLogs: frame truncado, logs posiblemente incompletos');
      break;
    }
  }
  return lines.join('').split('\n').slice(-tail).join('\n');
}

/**
 * Extrae el meta del job de los logs. El contenedor puede emitir una o más líneas
 * `<prefix>{json}` (p.ej. una con una URL de resultado, otra con una lista de pendientes).
 * Se MERGEAN (Object.assign en orden) para que campos de líneas distintas coexistan.
 * @param {string} logs
 * @param {string} [prefix=JOB_META_PREFIX]
 * @param {(meta:object)=>object} [sanitize] filtro opcional aplicado al meta final (p.ej.
 *   para descartar campos con esquemas de URL peligrosos antes de renderizarlos en un <a href>)
 * @returns {object|null}
 */
export function parseJobMeta(logs, prefix = JOB_META_PREFIX, sanitize) {
  let meta = null;
  for (const line of logs.split('\n')) {
    const i = line.indexOf(prefix);
    if (i === -1) continue;
    try {
      const parsed = JSON.parse(line.slice(i + prefix.length));
      meta = { ...(meta || {}), ...parsed };
    } catch {
      // línea corrupta — ignorar, conservar el meta anterior
    }
  }
  return meta && sanitize ? sanitize(meta) : meta;
}

/** Quita las líneas de meta de los logs visibles. */
export function stripJobMeta(logs, prefix = JOB_META_PREFIX) {
  return logs.split('\n').filter((l) => !l.includes(prefix)).join('\n');
}

/**
 * Parsea una línea buscando el marcador `<prefix>{json}`. Núcleo puro que un lector de
 * stream en vivo aplica a cada línea a medida que llega.
 * @param {string} line
 * @param {string} [prefix=JOB_STEP_PREFIX]
 * @returns {object|null} el objeto del marcador, o null si no hay marcador/JSON corrupto
 */
export function parseStepLine(line, prefix = JOB_STEP_PREFIX) {
  const i = line.indexOf(prefix);
  if (i === -1) return null;
  try { return JSON.parse(line.slice(i + prefix.length)); } catch { return null; }
}

/**
 * Busca en los logs la primera línea con `<prefix>[...]` y devuelve el array parseado.
 * Pensado para comandos "de listado" que un job read-only imprime al final (p.ej. filas
 * pendientes, clientes pendientes, negocios cargados) sin necesitar una API aparte.
 *
 * Una línea corrupta NO aborta: se sigue buscando en las siguientes (el proceso puede haber
 * escrito basura antes del marcador bueno). Sin marcador → [].
 * @param {string} logs
 * @param {string} prefix
 * @returns {any[]}
 */
export function parsePrefixedJsonArray(logs, prefix) {
  for (const line of String(logs ?? '').split('\n')) {
    const i = line.indexOf(prefix);
    if (i === -1) continue;
    try {
      const arr = JSON.parse(line.slice(i + prefix.length));
      if (Array.isArray(arr)) return arr;
    } catch {
      // línea corrupta — seguir buscando
    }
  }
  return [];
}
