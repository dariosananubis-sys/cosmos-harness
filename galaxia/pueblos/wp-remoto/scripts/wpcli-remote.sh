#!/usr/bin/env bash
# Ejecuta un comando wp-cli remoto en un servidor de una flota, resolviendo host/pass desde un
# secreto BWS tipo "mapa de servidores" y probando rutas PHP de Plesk en orden hasta encontrar
# una ejecutable. Uso:
#   wpcli-remote.sh <server-slug> <docroot> -- <wp-cli-args...>
# Requiere: sshpass, bws CLI, BWS_ACCESS_TOKEN en el entorno, y SERVERS_MAP_SECRET_ID (id de un
# secreto BWS con JSON `[{slug, sshHost, sshPort, sshUser, sshPass}, ...]`).
set -euo pipefail

SERVER_SLUG="$1"; shift
DOCROOT="$1"; shift
if [ "$1" != "--" ]; then
  echo "uso: wpcli-remote.sh <server-slug> <docroot> -- <wp-cli-args...>" >&2
  exit 2
fi
shift

: "${SERVERS_MAP_SECRET_ID:?define SERVERS_MAP_SECRET_ID=<id del secreto BWS con el mapa de servidores>}"
: "${BWS_ACCESS_TOKEN:?define BWS_ACCESS_TOKEN}"
export BWS_ACCESS_TOKEN

# Extraer host/port/user/pass del slug pedido, sin volcar el resto del mapa.
read -r SSH_HOST SSH_PORT SSH_USER SSH_PASS < <(
  bws secret get "$SERVERS_MAP_SECRET_ID" --output json | python3 -c "
import json, sys
d = json.load(sys.stdin)
v = json.loads(d['value'])
for s in v:
    if s.get('slug') == '${SERVER_SLUG}':
        print(s['sshHost'], s['sshPort'], s['sshUser'], s['sshPass'])
        break
"
)

if [ -z "${SSH_HOST:-}" ]; then
  echo "servidor no encontrado en el mapa: ${SERVER_SLUG}" >&2
  exit 3
fi

REMOTE_CMD_ARGS="$(printf ' %q' "$@")"
# Probar cada combinación (binario wp-cli, versión de PHP de Plesk) con un probe y usar la
# primera que responda. Ojo con `wp` como wrapper de shell en vez de binario ejecutable: si se
# le pasa a PHP directamente, PHP imprime el texto del wrapper y sale 0 SIN ejecutar nada — el
# script canta éxito y el comando nunca se aplicó (gotcha real: así se perdió en silencio un
# backfill porque el probe naive no distinguía "wp respondió" de "wp es un wrapper de shell").
# Ese mismo wrapper puede además hacer `$@` sin comillas, partiendo argumentos con espacios.
REMOTE_SCRIPT="cd $(printf '%q' "$DOCROOT") && for T in /usr/local/bin/wp-cli.phar /usr/local/bin/wp; do [ -f \"\$T\" ] || continue; for P in /opt/plesk/php/8.3/bin/php /opt/plesk/php/8.2/bin/php /opt/plesk/php/8.4/bin/php /opt/plesk/php/8.1/bin/php /opt/plesk/php/8.0/bin/php /opt/plesk/php/7.4/bin/php; do [ -x \"\$P\" ] || continue; \"\$P\" -d memory_limit=512M \"\$T\" --allow-root eval \"echo 'WPCLI_PROBE_OK';\" 2>/dev/null | grep -q WPCLI_PROBE_OK || continue; exec \"\$P\" -d memory_limit=512M \"\$T\" --allow-root${REMOTE_CMD_ARGS}; done; done; echo 'sin wp-cli ejecutable via PHP de Plesk' >&2; exit 127"

sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -p "$SSH_PORT" "${SSH_USER}@${SSH_HOST}" "$REMOTE_SCRIPT"
