// docker-secret-cookie-auth.js — login propio (página + cookie de sesión) para la UI web de
// un servicio, pensado para sustituir al basic_auth de un reverse proxy (popup feo del
// navegador, sin logout real). Sin deps externas: solo node:crypto y node:fs, http nativo.
//
// Contrato: handleAuth(req, res, url) -> 'pass' | 'handled'
//   'pass'    -> petición pública o autenticada; el caller sigue su routing.
//   'handled' -> este módulo ya escribió la respuesta; el caller debe `return`.
//
// Config por entorno (todas opcionales, con defaults razonables):
//   APP_PASSWORD / APP_PASSWORD_FILE  contraseña única del panel (secret-file preferido:
//                                     una env var con la password queda visible en `docker
//                                     inspect`; un secret-file en /run/secrets no)
//   APP_SESSION_TTL_MS                caducidad de sesión (default 30 días)
//   APP_NAME / APP_SUBTITLE           branding de la página de login
//   APP_LOGO_URI                      data: URI opcional para favicon + logo del login
import crypto from 'node:crypto';
import fs from 'node:fs';

const COOKIE_NAME = process.env.APP_COOKIE_NAME || 'app_session';
const APP_NAME = process.env.APP_NAME || 'PANEL';
const APP_SUBTITLE = process.env.APP_SUBTITLE || '';
const LOGO_URI = process.env.APP_LOGO_URI || '';
const MAX_BODY = 8 * 1024; // 8 KB — el form de login es minúsculo

// ─── Password (secret-file, nunca env por defecto: se filtra en docker inspect) ─
function loadPassword() {
  if (process.env.APP_PASSWORD) {
    // Path de debug: en prod se filtra en `docker inspect`; preferir secret-file.
    console.warn('[auth] APP_PASSWORD via env — NO usar en prod, preferir secret-file');
    return process.env.APP_PASSWORD.trim();
  }
  const file = process.env.APP_PASSWORD_FILE || '/run/secrets/app_password';
  try {
    return fs.readFileSync(file, 'utf8').trim();
  } catch {
    return null;
  }
}

const PASSWORD = loadPassword();
if (!PASSWORD) {
  console.warn('[auth] sin password configurada — acceso bloqueado salvo /healthz y /login');
}

const sha256 = (s) => crypto.createHash('sha256').update(s).digest('hex');
// Hash de la password, SOLO para validar el formulario de login en tiempo constante.
// No es el valor de la cookie: ver el bloque de sesiones más abajo.
const PASSWORD_HASH = PASSWORD ? sha256(PASSWORD) : null;

// Comparación en tiempo constante de dos hex de igual longitud (64 chars).
function passwordMatches(hashedInput) {
  if (!PASSWORD_HASH || typeof hashedInput !== 'string' || hashedInput.length !== PASSWORD_HASH.length) {
    return false;
  }
  return crypto.timingSafeEqual(Buffer.from(hashedInput), Buffer.from(PASSWORD_HASH));
}

// ─── Sesiones: token aleatorio por login, en memoria ─────────────────────────────
// La cookie NO debe ser un hash constante de la password: quien la copiara entraría para
// siempre, /logout solo la borraría del navegador (el valor seguiría siendo válido) y revocar
// una sesión filtrada exigiría cambiar la contraseña a todo el mundo. Cada login genera 32
// bytes aleatorios con vencimiento propio, así que se puede tirar una sesión concreta y
// caducan de verdad. Se guardan en memoria a propósito (pensado para paneles internos de
// pocos usuarios): evita tabla + migración; coste asumido: al recrear el proceso, todos
// vuelven a loguearse.
//
// El lookup en el Map no es de tiempo constante, y no hace falta: el token es aleatorio de
// 256 bits, no se deriva de ningún secreto adivinable.
const SESSION_TTL_MS = Number(process.env.APP_SESSION_TTL_MS || 30 * 24 * 60 * 60 * 1000);
const sessions = new Map(); // token -> epoch ms en que expira

function purgeExpiredSessions(now = Date.now()) {
  for (const [token, expiresAt] of sessions) {
    if (now > expiresAt) sessions.delete(token);
  }
}

function createSession() {
  purgeExpiredSessions(); // barrido perezoso: sin timers que mantengan vivo el event loop
  const token = crypto.randomBytes(32).toString('hex');
  sessions.set(token, Date.now() + SESSION_TTL_MS);
  return token;
}

function sessionValid(token) {
  if (typeof token !== 'string' || !token) return false;
  const expiresAt = sessions.get(token);
  if (expiresAt === undefined) return false;
  if (Date.now() > expiresAt) { sessions.delete(token); return false; }
  return true;
}

// ─── Rate-limit del login (endpoint público con TLS → protege fuerza bruta) ─────
// Ventana deslizante en memoria por IP (primer hop de X-Forwarded-For, que fija el proxy).
// Tras LOGIN_MAX fallos en LOGIN_WINDOW_MS → 429 hasta que expire. Se limpia al acertar.
const LOGIN_MAX = 8;
const LOGIN_WINDOW_MS = 10 * 60 * 1000;
const loginAttempts = new Map(); // ip -> { count, first }

function clientIp(req) {
  const xff = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  return xff || req.socket?.remoteAddress || 'unknown';
}
function loginBlocked(ip) {
  const e = loginAttempts.get(ip);
  if (!e) return false;
  if (Date.now() - e.first > LOGIN_WINDOW_MS) { loginAttempts.delete(ip); return false; }
  return e.count >= LOGIN_MAX;
}
function recordLoginFail(ip) {
  const e = loginAttempts.get(ip);
  if (!e || Date.now() - e.first > LOGIN_WINDOW_MS) loginAttempts.set(ip, { count: 1, first: Date.now() });
  else e.count += 1;
}

function parseCookies(header) {
  const out = {};
  if (!header) return out;
  for (const part of header.split(';')) {
    const i = part.indexOf('=');
    if (i < 0) continue;
    out[part.slice(0, i).trim()] = part.slice(i + 1).trim();
  }
  return out;
}

function sessionTokenOf(req) {
  return parseCookies(req.headers.cookie)[COOKIE_NAME];
}

function isAuthenticated(req) {
  return sessionValid(sessionTokenOf(req));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > MAX_BODY) reject(new Error('body demasiado grande'));
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

function extractPassword(body, contentType = '') {
  if (contentType.includes('application/json')) {
    try {
      return JSON.parse(body).password ?? '';
    } catch {
      return '';
    }
  }
  return new URLSearchParams(body).get('password') ?? '';
}

// ─── Respuestas ───────────────────────────────────────────────────────────────
function redirect(res, location) {
  res.writeHead(302, { Location: location });
  res.end();
}

function setSessionCookie(res, location) {
  const token = createSession();
  const maxAge = Math.floor(SESSION_TTL_MS / 1000);
  res.writeHead(302, {
    Location: location,
    'Set-Cookie': `${COOKIE_NAME}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`,
  });
  res.end();
}

// Invalida la sesión EN EL SERVIDOR además de borrar la cookie: si no, el token seguiría
// sirviendo para entrar a quien lo tuviera copiado y /logout sería puro teatro.
function clearSessionCookie(req, res, location) {
  sessions.delete(sessionTokenOf(req));
  res.writeHead(302, {
    Location: location,
    'Set-Cookie': `${COOKIE_NAME}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`,
  });
  res.end();
}

function sendLoginPage(res, { error = false } = {}) {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(loginHtml(error));
}

// ─── Página de login (tema oscuro minimal, sin dependencias externas) ───────────
function loginHtml(error) {
  const banner = error
    ? `<div class="error" role="alert">Contraseña incorrecta. Inténtalo de nuevo o avisa al administrador.</div>`
    : '';
  const logoImg = LOGO_URI ? `<img class="brand-logo" src="${LOGO_URI}" alt="${APP_NAME}" />` : '';
  const subtitle = APP_SUBTITLE ? `<p class="subtitle">${APP_SUBTITLE}</p>` : '';
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${APP_NAME} — Acceso</title>
  <!-- Sin fuentes de terceros: es la única página pública, y cargarlas filtraría a un tercero
       la IP de quien abre el login. Los font-stack de abajo caen a las del sistema. -->
  ${LOGO_URI ? `<link rel="icon" type="image/png" href="${LOGO_URI}" />` : ''}
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0b0b0c;
      color: #ececee;
      min-height: 100dvh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      -webkit-font-smoothing: antialiased;
    }
    .card {
      width: 100%;
      max-width: 360px;
      background: #161618;
      border: 1px solid #30303a;
      border-radius: 10px;
      box-shadow: 0 10px 30px -16px rgba(0,0,0,.8);
      padding: 1.75rem 1.5rem;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: .55rem;
      font-weight: 700;
      font-size: 1.05rem;
      letter-spacing: .26em;
      text-transform: uppercase;
      color: #c8a24b;
    }
    .brand-logo { height: 30px; width: 30px; object-fit: contain; flex-shrink: 0; }
    .subtitle {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      color: #a6a6b0;
      font-size: .78rem;
      letter-spacing: .02em;
      margin: .5rem 0 1.5rem;
    }
    form { display: flex; flex-direction: column; gap: .75rem; }
    .pw-wrap { position: relative; display: flex; }
    .pw-toggle { position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
      background: none; border: none; color: #a6a6b0; cursor: pointer; padding: .35rem .5rem;
      font-family: ui-monospace, monospace; font-size: .7rem; text-transform: uppercase; letter-spacing: .04em; }
    .pw-toggle:hover { color: #c8a24b; }
    .pw-toggle:focus-visible { outline: 2px solid #c8a24b; outline-offset: 2px; border-radius: 4px; }
    #password {
      width: 100%;
      min-height: 44px;
      padding: .65rem 4rem .65rem .75rem;
      border: 1px solid #30303a;
      border-radius: 6px;
      background: #1d1d20;
      font-size: 1rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      color: #ececee;
      outline: none;
      transition: border-color .15s, box-shadow .15s;
    }
    #password:focus { border-color: #c8a24b; box-shadow: 0 0 0 3px rgba(200,162,75,.28); }
    #password:focus-visible { border-color: #c8a24b; box-shadow: 0 0 0 3px rgba(200,162,75,.28); outline: none; }
    button {
      width: 100%;
      min-height: 44px;
      padding: .7rem;
      background: #c8a24b;
      color: #14120b;
      font-weight: 700;
      font-size: .8125rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      border: none;
      border-radius: 7px;
      cursor: pointer;
      transition: background .15s;
    }
    button:hover { background: #e0c074; }
    button:focus-visible { outline: 2px solid #c8a24b; outline-offset: 2px; }
    .error {
      background: rgba(240,106,94,.12);
      border: 1px solid rgba(240,106,94,.32);
      color: #f06a5e;
      border-radius: 8px;
      padding: .6rem .8rem;
      font-size: .875rem;
      margin-bottom: .75rem;
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
    }
  </style>
</head>
<body>
  <div class="card">
    <p class="brand">${logoImg}${APP_NAME}</p>
    ${subtitle}
    ${banner}
    <form method="POST" action="/login">
      <label for="password" style="font-size:.875rem;font-weight:500;color:#ececee;margin-bottom:-.25rem;">Contraseña</label>
      <div class="pw-wrap">
        <input type="password" id="password" name="password" autocomplete="current-password" autofocus required />
        <button type="button" class="pw-toggle" id="pw-toggle" aria-label="Mostrar contraseña">ver</button>
      </div>
      <button type="submit">Entrar</button>
    </form>
    <script>
      (function () {
        var i = document.getElementById('password'), b = document.getElementById('pw-toggle');
        b.addEventListener('click', function () {
          var show = i.type === 'password';
          i.type = show ? 'text' : 'password';
          b.textContent = show ? 'ocultar' : 'ver';
          b.setAttribute('aria-label', show ? 'Ocultar contraseña' : 'Mostrar contraseña');
          i.focus();
        });
      })();
    </script>
  </div>
</body>
</html>`;
}

// ─── Gate principal ─────────────────────────────────────────────────────────────
export async function handleAuth(req, res, url) {
  const path = url.pathname;
  const method = req.method;

  // /healthz siempre público (smoke / monitoring).
  if (method === 'GET' && path === '/healthz') return 'pass';

  // GET /login — formulario (o redirige si ya hay sesión).
  if (method === 'GET' && path === '/login') {
    if (isAuthenticated(req)) {
      redirect(res, '/');
      return 'handled';
    }
    sendLoginPage(res, { error: url.searchParams.has('error') });
    return 'handled';
  }

  // POST /login — valida y crea sesión (con rate-limit por IP).
  if (method === 'POST' && path === '/login') {
    const ip = clientIp(req);
    if (loginBlocked(ip)) {
      res.writeHead(429, { 'Content-Type': 'text/html; charset=utf-8', 'Retry-After': '600' });
      res.end('<!DOCTYPE html><meta charset="utf-8"><p>Demasiados intentos. Espera unos minutos.</p>');
      return 'handled';
    }
    let body;
    try {
      body = await readBody(req);
    } catch {
      redirect(res, '/login?error=1');
      return 'handled';
    }
    const password = extractPassword(body, req.headers['content-type'] || '');
    if (PASSWORD && passwordMatches(sha256(password))) {
      loginAttempts.delete(ip);
      setSessionCookie(res, '/');
    } else {
      recordLoginFail(ip);
      redirect(res, '/login?error=1');
    }
    return 'handled';
  }

  // GET /logout — cierra sesión (cookie + token en servidor).
  if (method === 'GET' && path === '/logout') {
    clearSessionCookie(req, res, '/login');
    return 'handled';
  }

  // Resto: exige sesión válida.
  if (isAuthenticated(req)) return 'pass';

  // No autenticado.
  if (!PASSWORD) {
    res.writeHead(503, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end('<!DOCTYPE html><meta charset="utf-8"><p>Acceso no configurado en el servidor.</p>');
    return 'handled';
  }
  const accept = req.headers.accept || '';
  if (path.startsWith('/api/') || accept.includes('application/json')) {
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'No autenticado' }));
    return 'handled';
  }
  redirect(res, '/login');
  return 'handled';
}
