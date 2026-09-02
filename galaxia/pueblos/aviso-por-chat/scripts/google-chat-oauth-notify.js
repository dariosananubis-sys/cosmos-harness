// google-chat-oauth-notify.js — DM a un equipo por Google Chat al terminar un job de fondo,
// usando credenciales OAuth de un USUARIO real (no una Service Account): útil cuando la app de
// Chat de tu Workspace solo tiene aprobado el flujo de usuario, o cuando quieres que los DM
// salgan "de parte de" una persona/bot conocido en vez de una cuenta de servicio genérica.
// Cero dependencias: Node 18+ trae `fetch` global.
//
// Credenciales (patrón secret-file, coherente con el resto de un control-plane que no dependa
// de un gestor de secretos externo): GCHAT_CREDENTIALS / GCHAT_TOKEN como JSON en env, o
// secret-files en GCHAT_CREDENTIALS_FILE / GCHAT_TOKEN_FILE (default /run/secrets/gchat_credentials
// y /run/secrets/gchat_token). Refresca el access token en cada llamada — con la app OAuth en
// modo "Producción" el refresh_token no caduca por uso.
//
// NUNCA lanza: una notificación fallida no debe tumbar el job que la dispara. Devuelve
// {ok, sent, errors}.
import { readFileSync } from 'node:fs';

const TOKEN_URI = 'https://oauth2.googleapis.com/token';
const CHAT = 'https://chat.googleapis.com/v1';

// Destinatarios SOLO desde env. Sin fallback hardcoded: si está ENABLED=1 pero la lista viene
// vacía, notifyTeam corta sin enviar — nadie recibe un mensaje por sorpresa por un valor
// olvidado en el código.
const RECIPIENTS = (process.env.GCHAT_NOTIFY_RECIPIENTS || '')
  .split(',').map((s) => s.trim()).filter(Boolean);
const ENABLED = process.env.GCHAT_NOTIFY_ENABLED !== '0';

function loadJson(envVar, fileEnv, defaultPath) {
  const raw = process.env[envVar];
  if (raw && raw.trim()) return JSON.parse(raw);
  const path = process.env[fileEnv] || defaultPath;
  return JSON.parse(readFileSync(path, 'utf8'));
}

async function postJson(url, body, headers) {
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`${url.split('/v1')[1] || url} → HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return res.json();
}

async function refreshAccessToken(creds, token) {
  const cfg = creds.installed || creds.web || creds;
  const params = new URLSearchParams({
    client_id: cfg.client_id,
    client_secret: cfg.client_secret,
    refresh_token: token.refresh_token,
    grant_type: 'refresh_token',
  });
  const res = await fetch(TOKEN_URI, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  });
  if (!res.ok) throw new Error(`token refresh HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return (await res.json()).access_token;
}

async function resolveDm(accessToken, email) {
  const headers = { Authorization: `Bearer ${accessToken}` };
  const q = new URLSearchParams({ name: `users/${email}` });
  const res = await fetch(`${CHAT}/spaces:findDirectMessage?${q}`, { headers });
  if (res.ok) return (await res.json()).name;
  if (res.status !== 404) throw new Error(`findDirectMessage HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const created = await postJson(`${CHAT}/spaces:setup`, {
    space: { spaceType: 'DIRECT_MESSAGE' },
    memberships: [{ member: { name: `users/${email}`, type: 'HUMAN' } }],
  }, { Authorization: `Bearer ${accessToken}`, 'Content-Type': 'application/json' });
  return created.name;
}

/**
 * Notifica al equipo el resultado de un job. Nunca lanza.
 * @param {{status:'completed'|'partial'|'failed', queue:string, label?:string, meta?:object, errorMsg?:string}} ev
 */
export async function notifyTeam(ev) {
  if (!ENABLED || RECIPIENTS.length === 0) return { ok: false, sent: 0, errors: ['disabled/no-recipients'] };
  try {
    const creds = loadJson('GCHAT_CREDENTIALS', 'GCHAT_CREDENTIALS_FILE', '/run/secrets/gchat_credentials');
    const token = loadJson('GCHAT_TOKEN', 'GCHAT_TOKEN_FILE', '/run/secrets/gchat_token');
    const accessToken = await refreshAccessToken(creds, token);
    const text = buildText(ev);
    const errors = [];
    let sent = 0;
    for (const email of RECIPIENTS) {
      try {
        const space = await resolveDm(accessToken, email);
        await postJson(`${CHAT}/${space}/messages`, { text },
          { Authorization: `Bearer ${accessToken}`, 'Content-Type': 'application/json' });
        sent++;
      } catch (e) { errors.push(`${email}: ${e.message}`); }
    }
    return { ok: errors.length === 0, sent, errors };
  } catch (e) {
    return { ok: false, sent: 0, errors: [e.message] };
  }
}

function buildText({ status, queue, label, meta, errorMsg }) {
  const icon = status === 'completed' ? '✅' : status === 'partial' ? '⚠️' : '❌';
  const word = status === 'completed' ? 'OK' : status === 'partial' ? 'CON ERRORES' : 'FALLÓ';
  const who = [meta?.razonSocial, meta?.domain].filter(Boolean).join(' · ');
  const head = `${icon} *${queue}* ${label ? `· ${label} ` : ''}${who ? `· ${who} ` : ''}— ${word}`;
  const lines = [head];
  if (status !== 'completed' && errorMsg) lines.push(`Motivo: ${errorMsg}`);
  if (meta?.driveUrl) lines.push(`Drive: ${meta.driveUrl}`);
  return lines.join('\n');
}
