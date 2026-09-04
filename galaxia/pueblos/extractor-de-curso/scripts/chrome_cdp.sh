#!/usr/bin/env bash
# Abre una copia del perfil real de Chrome con puerto CDP, para reutilizar
# la sesión ya iniciada del usuario sin pedirle credenciales.
#
# Chrome 136+ ignora --remote-debugging-port sobre el user-data-dir por defecto;
# por eso se copia el perfil antes de lanzarlo con el puerto CDP abierto.
#
#   ./chrome_cdp.sh abrir  [puerto]   -> lanza y deja el puerto escuchando
#   ./chrome_cdp.sh cerrar [puerto]   -> mata el proceso y BORRA la copia
#
# La copia contiene cookies de todas las cuentas del perfil: borrarla al acabar
# no es opcional.

set -euo pipefail

PUERTO="${2:-9223}"
ORIGEN="$HOME/Library/Application Support/Google/Chrome"
COPIA="${CURSO_CHROME_DIR:-/tmp/chrome-curso-$PUERTO}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

case "${1:-}" in
  abrir)
    [ -x "$CHROME" ] || { echo "No encuentro Google Chrome en $CHROME" >&2; exit 1; }
    [ -d "$ORIGEN/Default" ] || { echo "No encuentro el perfil en $ORIGEN" >&2; exit 1; }

    rm -rf "$COPIA"
    mkdir -p "$COPIA"
    cp "$ORIGEN/Local State" "$COPIA/" 2>/dev/null || true
    rsync -a \
      --exclude Cache --exclude 'Code Cache' --exclude GPUCache \
      --exclude 'Service Worker' --exclude 'Cache Storage' \
      "$ORIGEN/Default" "$COPIA/"

    "$CHROME" \
      --user-data-dir="$COPIA" \
      --remote-debugging-port="$PUERTO" \
      --no-first-run --no-default-browser-check \
      about:blank >/dev/null 2>&1 &

    for _ in $(seq 1 20); do
      if curl -sf "http://127.0.0.1:$PUERTO/json/version" >/dev/null; then
        echo "CDP listo en :$PUERTO (perfil: $COPIA)"
        echo "Al terminar:  $0 cerrar $PUERTO"
        exit 0
      fi
      sleep 0.5
    done
    echo "Chrome no expuso el puerto $PUERTO" >&2
    exit 1
    ;;
  cerrar)
    pkill -f "user-data-dir=$COPIA" 2>/dev/null || true
    sleep 1
    rm -rf "$COPIA"
    echo "Cerrado y copia de perfil borrada ($COPIA)"
    ;;
  *)
    echo "uso: $0 {abrir|cerrar} [puerto]" >&2
    exit 1
    ;;
esac
