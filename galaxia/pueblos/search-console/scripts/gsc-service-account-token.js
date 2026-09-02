// Acuña un access token del Service Account (SA_JSON) para leer una API de Google
// (Search Console, GA4, etc.): firma un JWT RS256 con la private_key y lo canjea en oauth2
// (grant jwt-bearer, con el scope que pidas). crypto nativo, sin dependencias.
// El canje es inyectable (`fetchToken`) para tests deterministas sin red.
//
// Sirve para cualquier API de Google que acepte OAuth2 Service Account con ese mismo grant:
// solo cambia el `scope` que le pases (webmasters.readonly, analytics.readonly, ...).
import crypto from 'node:crypto';

const DEFAULT_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly';
const DEFAULT_TOKEN_URI = 'https://oauth2.googleapis.com/token';
const b64url = (input) => Buffer.from(input).toString('base64url');

export async function serviceAccountAccessToken(saJson, {
  scope = DEFAULT_SCOPE,
  now = () => Math.floor(Date.now() / 1000),
  fetchToken,
} = {}) {
  const sa = typeof saJson === 'string' ? JSON.parse(saJson) : saJson;
  if (!sa?.client_email || !sa?.private_key) {
    throw new Error('Service Account JSON inválido: falta client_email o private_key');
  }
  const iat = now();
  const claim = {
    iss: sa.client_email,
    scope,
    aud: sa.token_uri || DEFAULT_TOKEN_URI,
    iat,
    exp: iat + 3600,
  };
  const unsigned = `${b64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }))}.${b64url(JSON.stringify(claim))}`;
  const signature = crypto.createSign('RSA-SHA256').update(unsigned).sign(sa.private_key);
  const assertion = `${unsigned}.${b64url(signature)}`;

  const doFetch = fetchToken ?? defaultTokenExchange;
  return doFetch(sa.token_uri || DEFAULT_TOKEN_URI, assertion);
}

async function defaultTokenExchange(tokenUri, assertion) {
  const res = await fetch(tokenUri, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion,
    }),
  });
  const json = await res.json().catch(() => null);
  if (!res.ok || !json?.access_token) {
    throw new Error(`Token exchange: HTTP ${res.status} ${json?.error ?? ''}`.trim());
  }
  return json.access_token;
}
