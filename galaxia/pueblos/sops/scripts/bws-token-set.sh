#!/usr/bin/env bash
# Fija un token de Bitwarden Secrets Manager (BWS) nuevo en un .env, lo VALIDA
# contra Bitwarden antes de escribir y solo lo guarda si autentica. El token se lee
# por STDIN (nunca por argumento: así no queda en `ps`, ni en el historial, ni en
# logs).
#
# Uso:
#   pbpaste | bws-token-set.sh <ruta/al/.env>     # pega el token que tengas en el portapapeles
#   bws-token-set.sh <ruta/al/.env> < fichero-con-token
#   echo -n '<token>' | bws-token-set.sh <ruta/al/.env>
#
# Asegúrate de que el .env de destino está en .gitignore: no se commitea el secreto.
set -euo pipefail

ENV="${1:?Uso: bws-token-set.sh <ruta/al/.env> (token por stdin)}"

command -v bws >/dev/null || { echo "falta el binario 'bws' (brew install bitwarden-secrets-manager)"; exit 1; }
[ -f "$ENV" ] || { echo "no existe $ENV"; exit 1; }

TOK="$(cat)"; TOK="${TOK//[$'\r\n\t ']/}"   # limpia saltos/espacios pegados sin querer
[ -n "$TOK" ] || { echo "no me has pasado ningún token por stdin"; exit 1; }

case "$TOK" in
  0.*.*) : ;;  # formato esperado: 0.<uuid>.<secret>
  *) echo "aviso: el token no tiene la forma 0.<uuid>.<secret>; sigo y dejo que bws decida" ;;
esac

echo "validando el token contra Bitwarden…"
TMP_OUT="$(mktemp)"; TMP_ERR="$(mktemp)"
if ! BWS_ACCESS_TOKEN="$TOK" bws secret list -o json >"$TMP_OUT" 2>"$TMP_ERR"; then
  echo "RECHAZADO — Bitwarden no acepta ese token:"
  sed -n '2p' "$TMP_ERR" | head -c 200; echo
  rm -f "$TMP_OUT" "$TMP_ERR"
  exit 2
fi
N="$(python3 -c "import json;print(len(json.load(open('$TMP_OUT'))))")"
rm -f "$TMP_OUT" "$TMP_ERR"
echo "OK — el token ve $N secretos."

# Sustituye la línea in-place conservando el resto del .env.
python3 - "$ENV" "$TOK" <<'PY'
import sys, io
env, tok = sys.argv[1], sys.argv[2]
lineas = io.open(env, encoding="utf-8").read().splitlines(keepends=True)
hecho = False
for i, l in enumerate(lineas):
    if l.startswith("BWS_ACCESS_TOKEN="):
        fin = "\n" if l.endswith("\n") else ""
        lineas[i] = f"BWS_ACCESS_TOKEN={tok}{fin}"
        hecho = True
        break
if not hecho:
    lineas.append(f"\nBWS_ACCESS_TOKEN={tok}\n")
io.open(env, "w", encoding="utf-8").write("".join(lineas))
print("escrito en", env)
PY

echo "listo. Si guardas también una copia cifrada de este .env en otro sitio,"
echo "recuerda refrescarla para que no diverjan."
