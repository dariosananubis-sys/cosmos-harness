#!/usr/bin/env bash
# wp-ssh.sh — wp-cli remoto por SSH con reutilización de sesión (ControlMaster) y
# ejecución de PHP segura (eval-file, nunca `wp eval` inline).
#
# Por qué existe: en un servidor con fail2ban, abrir una conexión SSH por comando
# acaba baneando la IP. ControlMaster mantiene una única conexión TCP y la reutiliza.
# Y `wp eval "<código>"` pasa el PHP como argumento de shell: cualquier comilla o
# carácter especial en el código lo rompe. Subir el fichero y hacer `wp eval-file`
# es la forma segura.
#
# Configuración (variables de entorno; ninguna es obligatoria si usas --sitio):
#   WP_SSH_HOST    host o IP del servidor
#   WP_SSH_USER    usuario SSH
#   WP_SSH_PASS    contraseña SSH (nunca se pasa por argumento: SSHPASS la lee del entorno)
#   WP_SSH_PORT    puerto SSH (por defecto 22)
#   WP_DOCROOT     ruta absoluta del WordPress en el servidor
#   WP_PHP_BIN     binario PHP a usar (por defecto "php" del PATH remoto)
#
# Alternativa: un índice JSON de sitios (--sitio <slug>, o $WP_SITES_JSON) con forma
#   { "sites": { "<slug>": { "ssh": { "host","user","pass","puerto","docroot","php" } } } }
# así una sola instalación de este script sirve a varios sitios sin tocar variables
# de entorno en cada llamada. Requiere `jq`.
#
# Uso:
#   wp-ssh.sh <args de wp-cli...>              # p.ej.  wp-ssh.sh plugin list
#   wp-ssh.sh --php <fichero.php>              # sube el fichero y hace eval-file
#   wp-ssh.sh --sitio <slug> <args de wp-cli...>
set -euo pipefail

PUERTO="${WP_SSH_PORT:-22}"
HOST="${WP_SSH_HOST:-}"
USUARIO="${WP_SSH_USER:-}"
CLAVE="${WP_SSH_PASS:-}"
DOCROOT="${WP_DOCROOT:-}"
PHP_BIN="${WP_PHP_BIN:-php}"

if [ "${1:-}" = "--sitio" ]; then
  SLUG="$2"; shift 2
  INDICE="${WP_SITES_JSON:-$HOME/.wp-sites/sites.json}"
  command -v jq >/dev/null || { echo "--sitio necesita jq (brew install jq)" >&2; exit 1; }
  [ -f "$INDICE" ] || { echo "no existe $INDICE" >&2; exit 1; }
  FICHA="$(jq -c --arg s "$SLUG" '.sites[$s] // .sites[($s | gsub("-";"."))]' "$INDICE")"
  [ "$FICHA" != "null" ] || { echo "'$SLUG' no está en $INDICE" >&2; exit 1; }
  HOST="$(jq -r '.ssh.host' <<<"$FICHA")"
  USUARIO="$(jq -r '.ssh.user // "root"' <<<"$FICHA")"
  CLAVE="$(jq -r '.ssh.pass // ""' <<<"$FICHA")"
  PUERTO="$(jq -r '.ssh.puerto // 22' <<<"$FICHA")"
  DOCROOT="$(jq -r '.ssh.docroot' <<<"$FICHA")"
  PHP_BIN="$(jq -r '.ssh.php // "php"' <<<"$FICHA")"
fi

[ -n "$HOST" ] && [ -n "$USUARIO" ] && [ -n "$DOCROOT" ] || {
  echo "faltan datos de conexión: define WP_SSH_HOST/WP_SSH_USER/WP_DOCROOT o usa --sitio <slug>" >&2
  exit 1
}

export SSHPASS="$CLAVE"
SSH_OPTS=(-p "$PUERTO" -o StrictHostKeyChecking=no -o LogLevel=ERROR
          -o ControlMaster=auto -o "ControlPath=/tmp/wp-ssh-%r@%h:%p" -o ControlPersist=300)
WP="$PHP_BIN /usr/local/bin/wp --allow-root --path=$DOCROOT"

if [ "${1:-}" = "--php" ]; then
  FICHERO="${2:?uso: wp-ssh.sh --php <fichero.php>}"
  [ -f "$FICHERO" ] || { echo "no existe el fichero PHP: $FICHERO" >&2; exit 2; }
  REMOTO="/tmp/wp-ssh-$$-$(basename "$FICHERO")"
  sshpass -e scp -P "$PUERTO" -o StrictHostKeyChecking=no -o LogLevel=ERROR "$FICHERO" \
    "$USUARIO@$HOST:$REMOTO" >/dev/null
  sshpass -e ssh "${SSH_OPTS[@]}" "$USUARIO@$HOST" "$WP eval-file $REMOTO; rm -f $REMOTO"
else
  sshpass -e ssh "${SSH_OPTS[@]}" "$USUARIO@$HOST" "$WP $(printf '%q ' "$@")"
fi
