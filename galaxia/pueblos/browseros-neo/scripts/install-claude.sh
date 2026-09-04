#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PREFLIGHT="$ROOT/scripts/preflight.py"
STATE_BASE=${XDG_STATE_HOME:-"$HOME/.local/state"}
STATE_DIR="$STATE_BASE/browseros-neo-vision-kit"
STATE_FILE="$STATE_DIR/install.json"
PENDING_FILE="$STATE_DIR/pending.json"
CLAUDE_CONFIG="$HOME/.claude.json"
SERVER_NAME=browseros-neo
MODE=${1:-}
shift || true
CONFIG_PATH=""
CONFIG_EXISTED=false
BACKUP=""
EXPECTED_URL=""
APPLY_ACTIVE=0

usage() {
  echo "Uso: $0 --check|--apply|--rollback [--config RUTA]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --config)
      [ "$#" -ge 2 ] || { usage >&2; exit 2; }
      CONFIG_PATH=$2
      shift 2
      ;;
    *) usage >&2; exit 2 ;;
  esac
done

require_tools() {
  command -v python3 >/dev/null || { echo "Falta python3" >&2; exit 2; }
  command -v claude >/dev/null || { echo "Falta Claude Code (comando claude)" >&2; exit 2; }
}

run_preflight() {
  if [ -n "$CONFIG_PATH" ]; then
    python3 "$PREFLIGHT" --config "$CONFIG_PATH" "$@"
  else
    python3 "$PREFLIGHT" "$@"
  fi
}

reject_symlink_path() {
  python3 - "$1" <<'PY'
import os, sys
from pathlib import Path
p = Path(sys.argv[1]).expanduser().absolute()
home = Path.home().absolute()
try:
    relative = p.relative_to(home)
except ValueError as exc:
    raise SystemExit(f"Ruta rechazada fuera del home: {p}") from exc
current = home
if current.is_symlink():
    raise SystemExit(f"Ruta rechazada por symlink: {current}")
for part in relative.parts:
    current = current / part
    if current.is_symlink():
        raise SystemExit(f"Ruta rechazada por symlink: {current}")
PY
}

mcp_snapshot() {
  MCP_OUTPUT=""
  MCP_CURRENT_URL=""
  MCP_CURRENT_TYPE=""
  MCP_CURRENT_SCOPE=""
  if ! MCP_OUTPUT=$(claude mcp get "$SERVER_NAME" 2>&1); then
    return 1
  fi
  MCP_CURRENT_URL=$(printf '%s\n' "$MCP_OUTPUT" | sed -n 's/^[[:space:]]*URL:[[:space:]]*//p' | head -n 1)
  MCP_CURRENT_TYPE=$(printf '%s\n' "$MCP_OUTPUT" | sed -n 's/^[[:space:]]*Type:[[:space:]]*//p' | head -n 1)
  MCP_CURRENT_SCOPE=$(printf '%s\n' "$MCP_OUTPUT" | sed -n 's/^[[:space:]]*Scope:[[:space:]]*//p' | head -n 1)
  [ -n "$MCP_CURRENT_URL" ]
}

mcp_matches() {
  [ "$MCP_CURRENT_URL" = "$1" ] &&
    [ "$MCP_CURRENT_TYPE" = http ] &&
    printf '%s\n' "$MCP_CURRENT_SCOPE" | grep -qi '^User'
}

mcp_absent_confirmed() {
  printf '%s\n' "$MCP_OUTPUT" | grep -Eqi '^[[:space:]]*(Error:[[:space:]]*)?No MCP server found( with name:.*)?[[:space:]]*$'
}

restore_config_if_safe() {
  if [ -n "$BACKUP" ] && [ -f "$BACKUP" ]; then
    if python3 - "$CLAUDE_CONFIG" "$BACKUP" <<'PY'
import json, sys
current_path, backup_path = sys.argv[1:]
try:
    with open(current_path, encoding="utf-8") as fh:
        current = json.load(fh)
    with open(backup_path, encoding="utf-8") as fh:
        backup = json.load(fh)
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
raise SystemExit(0 if current == backup or current == {} else 1)
PY
    then
      if ! cmp -s "$CLAUDE_CONFIG" "$BACKUP"; then
        cp -p "$BACKUP" "$CLAUDE_CONFIG"
      fi
    else
      echo "La configuración contiene otros cambios; se conserva. Copia previa: $BACKUP" >&2
      return 1
    fi
  elif [ "$CONFIG_EXISTED" = false ] && [ -f "$CLAUDE_CONFIG" ]; then
    python3 - "$CLAUDE_CONFIG" <<'PY'
import json, os, sys
path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)
if data == {}:
    os.unlink(path)
PY
  fi
  return 0
}

rollback_failed_apply() {
  status=$?
  trap - EXIT INT TERM
  set +e
  if [ "$APPLY_ACTIVE" = 1 ]; then
    CLEANUP_CONFIRMED=false
    if mcp_snapshot; then
      if mcp_matches "$EXPECTED_URL"; then
        if claude mcp remove "$SERVER_NAME" --scope user >/dev/null 2>&1; then
          if ! mcp_snapshot && mcp_absent_confirmed; then
            CLEANUP_CONFIRMED=true
          fi
        fi
      fi
    elif mcp_absent_confirmed; then
      CLEANUP_CONFIRMED=true
    fi
    if [ "$CLEANUP_CONFIRMED" = true ] && restore_config_if_safe; then
      rm -f "$PENDING_FILE"
    fi
  fi
  exit "$status"
}

mark_state_inactive() {
  python3 - "$STATE_FILE" <<'PY'
import json, os, sys
path = sys.argv[1]
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
data["created"] = False
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(data, fh)
    fh.write("\n")
os.chmod(tmp, 0o600)
os.replace(tmp, path)
PY
}

check_mode() {
  require_tools
  REPORT=$(run_preflight --json)
  printf '%s\n' "$REPORT"
  EXPECTED_URL=$(printf '%s\n' "$REPORT" | python3 -c 'import json, sys; print(json.load(sys.stdin)["mcp_url"])')
  if mcp_snapshot; then
    echo "claude_mcp_present=true"
    if mcp_matches "$EXPECTED_URL"; then
      echo "claude_mcp_matches_preflight=true"
    else
      echo "claude_mcp_matches_preflight=false"
    fi
  else
    if mcp_absent_confirmed; then
      echo "claude_mcp_present=false"
    else
      echo "claude_mcp_status=error" >&2
      return 6
    fi
  fi
}

apply_mode() {
  require_tools
  EXPECTED_URL=$(run_preflight --field mcp_url)
  case "$EXPECTED_URL" in
    http://127.0.0.1:*/*|http://localhost:*/*|http://\[::1\]:*/*) ;;
    *) echo "Endpoint MCP rechazado: no es loopback HTTP" >&2; exit 3 ;;
  esac

  if [ -e "$PENDING_FILE" ] || [ -L "$PENDING_FILE" ]; then
    echo "Hay una instalación previa interrumpida; ejecuta --rollback antes de continuar." >&2
    exit 7
  fi

  if mcp_snapshot; then
    if mcp_matches "$EXPECTED_URL"; then
      echo "browseros-neo ya está configurado con la URL correcta; sin cambios."
      return 0
    fi
    echo "browseros-neo ya existe con otra configuración; no se sobrescribe." >&2
    exit 4
  elif ! mcp_absent_confirmed; then
    echo "No se pudo determinar si browseros-neo existe; no se modifica nada." >&2
    exit 6
  fi

  reject_symlink_path "$STATE_DIR"
  reject_symlink_path "$STATE_FILE"
  reject_symlink_path "$STATE_FILE.tmp"
  reject_symlink_path "$PENDING_FILE"
  reject_symlink_path "$PENDING_FILE.tmp"
  reject_symlink_path "$CLAUDE_CONFIG"
  mkdir -p "$STATE_DIR"
  chmod 700 "$STATE_DIR"

  if [ -f "$CLAUDE_CONFIG" ]; then
    CONFIG_EXISTED=true
    BACKUP=$(mktemp "$STATE_DIR/claude-json-before.backup.XXXXXX")
    cp -p "$CLAUDE_CONFIG" "$BACKUP"
    chmod 600 "$BACKUP"
  fi

  python3 - "$PENDING_FILE" "$EXPECTED_URL" "$BACKUP" "$CONFIG_EXISTED" <<'PY'
import json, os, sys
path, url, backup, existed = sys.argv[1:]
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump({"server": "browseros-neo", "url": url, "backup": backup, "config_existed": existed == "true"}, fh)
    fh.write("\n")
os.chmod(tmp, 0o600)
os.replace(tmp, path)
PY
  APPLY_ACTIVE=1
  trap 'rollback_failed_apply' EXIT
  trap 'exit 130' INT TERM

  if ! claude mcp add --transport http --scope user "$SERVER_NAME" "$EXPECTED_URL"; then
    exit 5
  fi

  if ! mcp_snapshot || ! mcp_matches "$EXPECTED_URL"; then
    echo "La verificación MCP falló; se inicia rollback." >&2
    exit 6
  fi

  python3 - "$STATE_FILE" "$EXPECTED_URL" "$BACKUP" "$CONFIG_EXISTED" <<'PY'
import json, os, sys
path, url, backup, existed = sys.argv[1:]
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump({"created": True, "server": "browseros-neo", "url": url, "backup": backup, "config_existed": existed == "true"}, fh)
    fh.write("\n")
os.chmod(tmp, 0o600)
os.replace(tmp, path)
PY
  rm -f "$PENDING_FILE"
  APPLY_ACTIVE=0
  trap - EXIT INT TERM
  echo "browseros-neo añadido y verificado. Abre una sesión nueva de Claude Code."
}

rollback_mode() {
  require_tools
  reject_symlink_path "$STATE_FILE"
  reject_symlink_path "$STATE_FILE.tmp"
  reject_symlink_path "$PENDING_FILE"
  reject_symlink_path "$PENDING_FILE.tmp"
  RECOVERY=false
  if [ -f "$PENDING_FILE" ]; then
    LEDGER_FILE=$PENDING_FILE
    RECOVERY=true
  elif [ -f "$STATE_FILE" ]; then
    LEDGER_FILE=$STATE_FILE
  else
    echo "No hay estado que demuestre que este kit creó la entrada; no se elimina nada." >&2
    exit 4
  fi
  LEDGER_INFO=$(python3 - "$LEDGER_FILE" "$RECOVERY" <<'PY'
import json, sys
path, recovery = sys.argv[1:]
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
valid = data.get("server") == "browseros-neo" and isinstance(data.get("url"), str)
if recovery != "true":
    valid = valid and data.get("created") is True
url = data.get("url", "")
backup = data.get("backup", "")
if not isinstance(backup, str) or any(c in url + backup for c in "\r\n\t"):
    valid = False
print("yes" if valid else "no")
print(url)
print(backup)
print("true" if data.get("config_existed") is True else "false")
PY
)
  CREATED=$(printf '%s\n' "$LEDGER_INFO" | sed -n '1p')
  EXPECTED_URL=$(printf '%s\n' "$LEDGER_INFO" | sed -n '2p')
  BACKUP=$(printf '%s\n' "$LEDGER_INFO" | sed -n '3p')
  CONFIG_EXISTED=$(printf '%s\n' "$LEDGER_INFO" | sed -n '4p')
  if [ "$CREATED" != yes ]; then
    echo "Estado no autoritativo; no se elimina nada." >&2
    exit 4
  fi
  case "$EXPECTED_URL" in
    http://127.0.0.1:*/*|http://localhost:*/*|http://\[::1\]:*/*) ;;
    *) echo "Estado no autoritativo; URL local inválida." >&2; exit 4 ;;
  esac
  if [ -n "$BACKUP" ]; then
    case "$BACKUP" in
      "$STATE_DIR"/claude-json-before.backup.*) reject_symlink_path "$BACKUP" ;;
      *) echo "Estado no autoritativo; copia previa inválida." >&2; exit 4 ;;
    esac
  fi
  if [ "$RECOVERY" = true ] && [ "$CONFIG_EXISTED" = true ] && [ ! -f "$BACKUP" ]; then
    echo "Recuperación pendiente: falta la copia previa declarada; no se elimina nada." >&2
    exit 4
  fi
  if [ "$RECOVERY" = true ]; then
    if mcp_snapshot; then
      if ! mcp_matches "$EXPECTED_URL"; then
        echo "La entrada MCP cambió durante la instalación interrumpida; no se elimina nada." >&2
        exit 4
      fi
      claude mcp remove "$SERVER_NAME" --scope user >/dev/null
      if mcp_snapshot; then
        echo "Claude todavía declara la entrada tras retirarla; recuperación pendiente." >&2
        exit 6
      elif ! mcp_absent_confirmed; then
        echo "No se pudo confirmar la retirada; se conserva pending.json." >&2
        exit 6
      fi
    elif ! mcp_absent_confirmed; then
      echo "No se pudo determinar el estado MCP; se conserva pending.json." >&2
      exit 6
    fi
    if ! restore_config_if_safe; then
      echo "No se pudo cerrar la recuperación automática; se conserva pending.json." >&2
      exit 6
    fi
    if [ -f "$STATE_FILE" ]; then
      mark_state_inactive
    fi
    rm -f "$PENDING_FILE"
    echo "Instalación interrumpida recuperada. Neo y su perfil no se han tocado."
    return 0
  fi
  if ! mcp_snapshot || ! mcp_matches "$EXPECTED_URL"; then
    echo "La entrada MCP cambió desde la instalación; no se elimina nada." >&2
    exit 4
  fi
  claude mcp remove "$SERVER_NAME" --scope user >/dev/null
  if mcp_snapshot; then
    echo "Claude todavía declara la entrada tras retirarla; estado conservado." >&2
    exit 6
  elif ! mcp_absent_confirmed; then
    echo "No se pudo confirmar la retirada; estado conservado." >&2
    exit 6
  fi
  mark_state_inactive
  rm -f "$PENDING_FILE"
  echo "Entrada MCP retirada. Neo y su perfil no se han tocado."
}

case "$MODE" in
  --check) check_mode ;;
  --apply) apply_mode ;;
  --rollback) rollback_mode ;;
  *) usage; exit 2 ;;
esac
