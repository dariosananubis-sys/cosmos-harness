#!/usr/bin/env bash
# Abre Claude Code con la cuenta ELEGIDA. Compañero de claude-cuenta.py (gestor de
# sesiones aisladas por cuenta) — este script solo hace el arranque.
#
# Por qué existe: cada proceso de Claude Code gasta la cuota de la credencial que
# tenga cargada. Arrancando siempre por aquí, todas las ventanas gastan la misma
# cuenta — la elegida — y las demás cuentas se quedan iniciadas pero en reposo,
# con gasto cero. Además no se toca el Keychain compartido, que es lo que puede
# revocar sesiones cuando dos ventanas rotan token a la vez.
#
# Requiere: un directorio de "sesiones" (uno por cuenta, cada uno con su propio
# .claude.json / .credentials.json) gestionado por claude-cuenta.py. Configúralo
# con la variable de entorno CLAUDE_ACCOUNTS_DIR (por defecto ~/.claude-accounts).
#
# Uso:
#   ./claude-cuenta.sh                # abre la cuenta elegida
#   ./claude-cuenta.sh trabajo        # abre esa cuenta, sin cambiar la elegida
#   ./claude-cuenta.sh trabajo --model opus   # el resto de flags pasa a claude
#
# Cómodo: crea un alias en tu shell rc apuntando a la ruta real de este script.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORE="${CLAUDE_ACCOUNTS_DIR:-$HOME/.claude-accounts}"
SESSIONS="$STORE/sessions"

alias_pedido="${1:-}"
if [ -n "$alias_pedido" ] && [ -f "$STORE/$alias_pedido.json" ]; then
  shift
elif [ -n "$alias_pedido" ] && [ "${alias_pedido#-}" = "$alias_pedido" ]; then
  # Primer argumento que no empieza por "-" y no es una cuenta: es un alias mal
  # escrito. Cortar aquí es la diferencia entre avisar y abrir en silencio OTRA
  # cuenta — justo lo que este script existe para evitar.
  echo "No hay ninguna cuenta guardada como '$alias_pedido'." >&2
  echo "Guardadas:" >&2
  python3 "$REPO/claude-cuenta.py" lista >&2
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
  python3 "$REPO/claude-cuenta.py" lista >&2
  echo >&2
  echo "  python3 claude-cuenta.py elegir <alias>" >&2
  exit 1
fi

# Regenera el directorio aislado por si faltan enlaces (no pisa credenciales vivas).
python3 "$REPO/claude-cuenta.py" lanzar "$alias_pedido" >/dev/null

DEST="$SESSIONS/$alias_pedido"

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
  echo "Prepárala con:  python3 claude-cuenta.py relogin $alias_pedido" >&2
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
