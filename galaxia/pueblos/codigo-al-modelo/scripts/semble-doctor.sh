#!/usr/bin/env bash
# semble-doctor — deja semble instalado y usable, SIEMPRE sin su servidor MCP.
# Idempotente y seguro: se puede correr las veces que haga falta, en cualquier Mac.
#   scripts/semble-doctor.sh              # instala si falta, verifica, informa
#   scripts/semble-doctor.sh --quiet      # silencioso (para el hook de SessionStart)
#   scripts/semble-doctor.sh --warm ./tools ./src/mi-proyecto   # pre-indexa rutas
#
# Por qué existe: semble es un CLI, no un demonio. "Activarlo para siempre" = que el binario
# esté presente y que NUNCA se cuele su MCP (que se cargaría en cada sesión). Este script
# garantiza ambas cosas por mecanismo, no "si me acuerdo".
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

QUIET=0; WARM=()
while [ $# -gt 0 ]; do
  case "$1" in
    --quiet) QUIET=1 ;;
    --warm)  shift; [ $# -gt 0 ] && WARM+=("$1") ;;
    *) ;;
  esac
  shift
done
say() { [ "$QUIET" = 1 ] || printf '%s\n' "$*"; }

# 1. uv (gestor con el que se instala semble) — no cuesta dinero
if ! command -v uv >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then say "· instalando uv (brew)…"; brew install uv >/dev/null 2>&1 || true; fi
fi

# 2. semble
if ! command -v semble >/dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then say "· instalando semble…"; uv tool install "semble[mcp]" >/dev/null 2>&1 || true; fi
fi

# 3. NUNCA su MCP colgado en ~/.claude.json (se cargaría en todas las sesiones)
CJ="$HOME/.claude.json"
if [ -f "$CJ" ] && grep -q '"semble"' "$CJ" 2>/dev/null; then
  say "· quitando MCP semble colado en ~/.claude.json…"
  python3 - "$CJ" <<'PY' 2>/dev/null || true
import json, sys
p = sys.argv[1]
d = json.load(open(p))
def strip(o):
    ms = o.get('mcpServers')
    if isinstance(ms, dict):
        ms.pop('semble', None)
strip(d)
for pr in (d.get('projects') or {}).values():
    if isinstance(pr, dict):
        strip(pr)
json.dump(d, open(p, 'w'), indent=2)
PY
fi

# 4. Estado
if command -v semble >/dev/null 2>&1; then
  MCP=$( { grep -c '"semble"' "$CJ" 2>/dev/null || true; } | head -1 )
  say "OK  semble $(semble --version 2>/dev/null)  ·  MCP colado: ${MCP:-0}  (debe ser 0)"
else
  say "PENDIENTE  semble aún no disponible (instalación en curso, o falta uv/brew)"
  exit 1
fi

# 5. Pre-warm opcional (evita el ~1-2 min de la 1ª búsqueda que haría saltar a grep)
if [ "${#WARM[@]}" -gt 0 ]; then
  for w in "${WARM[@]}"; do
    [ -d "$w" ] && { say "· pre-warm ${w} ..."; semble search "warm index" "$w" --top-k 1 >/dev/null 2>&1 || true; }
  done
fi
exit 0
