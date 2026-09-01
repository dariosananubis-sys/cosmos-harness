// pg-secret-file-connection.js — construye el connection string de Postgres a partir de un
// Docker secret-file, nunca de una env var con la password en claro (una env var queda
// visible en `docker inspect`; un secret-file montado en /run/secrets no).
//
// DATABASE_URL sigue existiendo como override explícito para tests/desarrollo local, pero
// avisa por consola: en producción esa variable también es visible en `docker inspect`, así
// que no debería ser la fuente real de la contraseña ahí.
import defaultFs from 'node:fs';

/**
 * @param {object} [opts]
 * @param {string} [opts.passwordFile] ruta al secret-file (default: PG_PASSWORD_FILE o
 *   '/run/secrets/pg_password')
 * @param {typeof import('node:fs')} [opts.fs] inyectable para tests (evita tocar disco real)
 * @returns {string} postgres://user:pass@host:port/db
 */
export function buildPgConnectionString({ passwordFile, fs = defaultFs } = {}) {
  if (process.env.DATABASE_URL) {
    console.warn('[pg-secret-file-connection] DATABASE_URL override activo — no usar en prod (visible en `docker inspect`)');
    return process.env.DATABASE_URL;
  }
  const pwFile = passwordFile || process.env.PG_PASSWORD_FILE || '/run/secrets/pg_password';
  const password = fs.readFileSync(pwFile, 'utf8').trim();
  const host = process.env.PG_HOST || 'localhost';
  const port = process.env.PG_PORT || '5432';
  const user = process.env.PG_USER || 'postgres';
  const db = process.env.PG_DB || 'postgres';
  return `postgres://${user}:${encodeURIComponent(password)}@${host}:${port}/${db}`;
}
