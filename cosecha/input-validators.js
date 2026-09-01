// input-validators.js — validadores puros de entrada (boundary de un server HTTP).
// Dep-free a propósito (solo node:path): pensado para poder testear la lógica de validación
// sin arrastrar el resto de la app (DB, colas...) a la suite de tests.
import { join, relative, isAbsolute } from 'node:path';

// UUID (formato laxo 36 chars hex+guiones — vale para el uuid de Postgres/uuid-ossp).
export function isValidUuid(id) {
  return typeof id === 'string' && /^[0-9a-f-]{36}$/i.test(id);
}

// Slug: minúsculas/números/guiones, 2-80 — para ids legibles en URLs/paths (negocio, sitio...).
export function isValidSlug(s) {
  return typeof s === 'string' && /^[a-z0-9-]{2,80}$/i.test(s);
}

// Enlace seguro para render en href: solo https:// (bloquea javascript:, data:, etc — evita
// que una URL que viene de una fuente no confiable (logs de un contenedor, un formulario)
// acabe siendo un vector XSS al pintarla como enlace).
export function isSafeHttpsUrl(u) {
  return typeof u === 'string' && /^https:\/\//i.test(u);
}

// Valida un rango {inicio, fin} de un lote (p.ej. filas de una hoja a procesar en batch).
// Devuelve el mensaje de error (string) o null si es válido.
export function validateBatchRange(inicio, fin, { max = 200 } = {}) {
  const valido = (n) => typeof n === 'number' && Number.isInteger(n) && n >= 1;
  if (!valido(inicio) || !valido(fin) || fin < inicio) {
    return 'Rango inválido: inicio y fin deben ser enteros >= 1 con fin >= inicio.';
  }
  if (fin - inicio + 1 > max) {
    return `Máximo ${max} elementos por lote.`;
  }
  return null;
}

// Resuelve de forma segura una subcarpeta dentro de un mount/directorio base. Devuelve la
// ruta absoluta o null si escaparía del mount. Más robusto que comprobar con startsWith de
// string (vulnerable a directorios hermanos con el mismo prefijo, p.ej. `/exports-secret`
// pasando el check de `/exports`): usa path.relative y rechaza '..'/absolutos/vacío (lo que
// también evita listar el propio mount raíz).
export function safeSubdir(mount, name) {
  if (!name || typeof name !== 'string') return null;
  const dir = join(mount, name);
  const rel = relative(mount, dir);
  if (!rel || rel.startsWith('..') || isAbsolute(rel)) return null;
  return dir;
}
