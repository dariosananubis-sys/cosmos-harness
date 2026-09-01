#!/usr/bin/env bash
# Abre Claude Code con la cuenta ELEGIDA (una carpeta de config aislada por cuenta).
#
# Por qué existe: cada proceso de Claude Code gasta la cuota de la credencial que
# tenga cargada. Arrancando siempre por aquí, todas las ventanas gastan la misma
# cuenta — la elegida — y las demás cuentas se quedan iniciadas pero en reposo,
# con gasto cero. Además no se toca el Keychain compartido, que es lo que puede
# revocar sesiones cuando dos ventanas rotan token a la vez.
#
# Requiere: un directorio de "sesiones" con una subcarpeta por cuenta, cada una con
# su propio .claude.json / .credentials.json (créala iniciando sesión una vez con
# CLAUDE_CONFIG_DIR=<esa carpeta> claude). Configúralo con la variable de entorno
# CLAUDE_ACCOUNTS_DIR (por defecto ~/.claude-accounts). Guarda la cuenta por defecto
# escribiendo su alias en "$CLAUDE_ACCOUNTS_DIR/elegida".
#
# Uso:
#   ./claude-cuenta.sh                # abre la cuenta elegida
#   ./claude-cuenta.sh trabajo        # abre esa cuenta, sin cambiar la elegida
#   ./claude-cuenta.sh trabajo --model opus   # el resto de flags pasa a claude
#
# Cómodo: crea un alias en tu shell rc apuntando a la ruta real de este script.

set -euo pipefail

STORE="${CLAUDE_ACCOUNTS_DIR:-$HOME/.claude-accounts}"
SESSIONS="$STORE/sessions"

listar_cuentas() {
  [ -d "$SESSIONS" ] && find "$SESSIONS" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null
}

alias_pedido="${1:-}"
if [ -n "$alias_pedido" ] && [ -d "$SESSIONS/$alias_pedido" ]; then
  shift
elif [ -n "$alias_pedido" ] && [ "${alias_pedido#-}" = "$alias_pedido" ]; then
  # Primer argumento que no empieza por "-" y no es una cuenta conocida: es un alias
  # mal escrito. Cortar aquí es la diferencia entre avisar y abrir en silencio OTRA
  # cuenta — justo lo que este script existe para evitar.
  echo "No hay ninguna cuenta guardada como '$alias_pedido'." >&2
  echo "Guardadas:" >&2
  listar_cuentas >&2
  exit 1
else
  alias_pedido=""
fi

if [ -z "$alias_pedido" ]; then
  if [ -f "$STORE/elegida" ]; then
    alias_pedido="$(tr -d '[:space:]' < "$STORE/elegida")"
  fi
fi

if [ -z "$alias_pedido" ]; then
  echo "No hay cuenta elegida todavía. Elige una:" >&2
  listar_cuentas >&2
  echo >&2
  echo "  echo <alias> > \"$STORE/elegida\"" >&2
  exit 1
fi

DEST="$SESSIONS/$alias_pedido"
if [ ! -d "$DEST" ]; then
  echo "No existe la carpeta de sesión '$DEST'." >&2
  echo "Créala iniciando sesión una vez: CLAUDE_CONFIG_DIR=\"$DEST\" claude" >&2
  exit 1
fi

# Una sesión está lista de dos maneras: sembrada desde el almacén
# (.credentials.json) o con login propio, que NO deja fichero — Claude Code guarda
# ese token en su item de Keychain "Claude Code-credentials-<hash>" y solo deja la
# ficha oauthAccount en el .claude.json del directorio. Mirar solo el fichero daba
# "no tiene credenciales guardadas" sobre una cuenta perfectamente iniciada.
lista=0
[ -f "$DEST/.credentials.json" ] && lista=1
if [ "$lista" = "0" ] && [ -f "$DEST/.claude.json" ]; then
  python3 - "$DEST/.claude.json" <<'PY' && lista=1
import json, sys
try:
    acc = json.load(open(sys.argv[1])).get("oauthAccount") or {}
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if acc.get("accountUuid") else 1)
PY
fi

if [ "$lista" = "0" ]; then
  echo "La cuenta '$alias_pedido' no tiene sesión iniciada." >&2
  echo "Prepárala con:  CLAUDE_CONFIG_DIR=\"$DEST\" claude   (y haz login)" >&2
  exit 1
fi

# Variables que marcan "soy sesión hija de otro Claude". Si se heredan (p.ej. la
# ventana la abre otra sesión por osascript), la nueva arranca con el guardado de
# transcript APAGADO y compartiendo el canal de mensajería del padre: al reiniciar
# se pierde todo lo hablado.
sin_padre=()
for v in CLAUDE_CODE_CHILD_SESSION CLAUDECODE CLAUDE_CODE_SESSION_ID CLAUDE_PID \
         CLAUDE_CODE_ENTRYPOINT CLAUDE_CODE_MESSAGING_SOCKET \
         CLAUDE_CODE_MESSAGING_TOKEN CLAUDE_CODE_EXECPATH CLAUDE_EFFORT; do
  sin_padre+=(-u "$v")
done

# Bypass de permisos opcional (desactivado por defecto: actívalo solo si tu flujo
# de trabajo lo pide). Escape: CC_SIN_BYPASS=1 ./claude-cuenta.sh <alias>
bypass=()
[ -n "${CC_CON_BYPASS:-}" ] && bypass=(--dangerously-skip-permissions)
[ -n "${CC_SIN_BYPASS:-}" ] && bypass=()
case " $* " in
  *" --dangerously-skip-permissions "*|*" --permission-mode "*) bypass=() ;;
esac

exec env "${sin_padre[@]}" CLAUDE_CONFIG_DIR="$DEST" claude "${bypass[@]}" "$@"
