#!/usr/bin/env bash
# wp-mcp-stdio-bridge.sh — sirve por STDIO el MCP de Elementor (plugin EMCP Tools) de
# una web cuyo vhost va en una versión de PHP demasiado vieja para el propio plugin.
#
# El plugin EMCP Tools exige PHP 8.1+; si el vhost va por debajo, el endpoint HTTP
# normal responde 404 aunque el plugin esté activo (no falta la ruta: el plugin no
# llega a cargarse). Este puente no toca el PHP del vhost: usa el PHP >= 8.1 del CLI
# del servidor (uno de los binarios en $PHP_CANDIDATOS) solo para lanzar wp-cli, que
# expone el MCP por stdio. Así Claude usa los controles nativos de Elementor
# (containers, flexbox, theme templates) en vez de escribir _elementor_data a pelo.
#
# Configuración por variables de entorno:
#   WP_SSH_HOST, WP_SSH_USER, WP_SSH_PASS   credenciales SSH
#   WP_SSH_PORT     puerto SSH (por defecto 22)
#   WP_DOCROOT      ruta absoluta del WordPress en el servidor
#   WP_MCP_SERVER   nombre del servidor MCP registrado por el plugin
#                   (por defecto "emcp-tools-server")
#   PHP_CANDIDATOS  binarios PHP >= 8.1 a probar en el servidor, de más a menos
#                   reciente (por defecto "php8.4 php8.3 php8.2 php8.1")
#
# Uso:  wp-mcp-stdio-bridge.sh [usuario_wp]     (usuario_wp por defecto: 1)
set -euo pipefail

USUARIO_WP="${1:-1}"
HOST="${WP_SSH_HOST:?falta WP_SSH_HOST}"
USER_SSH="${WP_SSH_USER:?falta WP_SSH_USER}"
export SSHPASS="${WP_SSH_PASS:?falta WP_SSH_PASS}"
PUERTO="${WP_SSH_PORT:-22}"
DOCROOT="${WP_DOCROOT:?falta WP_DOCROOT}"
SERVIDOR_MCP="${WP_MCP_SERVER:-emcp-tools-server}"
CANDIDATOS="${PHP_CANDIDATOS:-php8.4 php8.3 php8.2 php8.1}"

# Resuelve el PHP >= 8.1 disponible EN EL SERVIDOR (no todos tienen la misma versión
# instalada como CLI): probar de mayor a menor evita fijar una versión que no exista
# en un servidor concreto.
ELIGE_PHP="for v in $CANDIDATOS; do command -v \"\$v\" >/dev/null 2>&1 && PHPBIN=\"\$v\" && break; done; [ -n \"\${PHPBIN:-}\" ] || { echo 'sin PHP >= 8.1 en el PATH de este servidor' >&2; exit 1; }"

exec sshpass -e ssh -p "$PUERTO" \
  -o StrictHostKeyChecking=no \
  -o ControlMaster=auto -o "ControlPath=/tmp/wp-mcp-%r@%h:%p" -o ControlPersist=600 \
  "$USER_SSH@$HOST" \
  "$ELIGE_PHP; \"\$PHPBIN\" -d memory_limit=512M /usr/local/bin/wp --allow-root --path=$DOCROOT mcp-adapter serve --server=$SERVIDOR_MCP --user=$USUARIO_WP"
