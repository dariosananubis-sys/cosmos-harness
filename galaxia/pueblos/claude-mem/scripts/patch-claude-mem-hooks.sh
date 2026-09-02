#!/usr/bin/env bash
# Parches de claude-mem tras cada actualización del plugin.
#
# 1. Silencia los hooks SessionStart:startup envolviendo los comandos en
#    `{ ... } 2>/dev/null; exit 0` para evitar el error UI
#    "Failed with non-blocking status code" cuando el worker bun tarda.
# 2. Arregla el bug del Agent SDK bundled que emite `--setting-sources ""`
#    sin valor, haciendo que `--permission-mode` lo consuma como valor y
#    rompa todas las observaciones con "Claude Code process exited with code 1"
#    (regresión que vuelve al bundled SDK pese al fix de v12.1.6 — afecta a
#    Claude Code 2.1.109+). Idempotente.
# 3. Alinea el puerto del health-check con CLAUDE_MEM_WORKER_PORT de
#    ~/.claude-mem/settings.json. Sin este parche los hooks chequean
#    37700+(uid%100) pero el worker escucha el puerto de settings (37777),
#    gatillando timeouts y la ausencia de context injection en SessionStart.
#    Reduce además el loop curl de 20s a 5s.
#
# Reaplicar manualmente tras cada `claude-mem` update o dejar que se ejecute
# desde un hook PostToolUse / alias post-install.
set -euo pipefail

HOOKS_DIR="$HOME/.claude/plugins/cache/thedotmack/claude-mem"
LATEST=$(ls -dt "$HOOKS_DIR"/[0-9]*/ 2>/dev/null | head -1)
LATEST="${LATEST%/}"
HOOKS_FILE="$LATEST/hooks/hooks.json"
WORKER_FILE="$LATEST/scripts/worker-service.cjs"

[ -f "$HOOKS_FILE" ] || { echo "hooks.json no encontrado en $LATEST"; exit 1; }
[ -f "$WORKER_FILE" ] || { echo "worker-service.cjs no encontrado en $LATEST"; exit 1; }

# --- Parche 1: silenciar TODOS los hooks SessionStart:startup (incl. smart-install) ---
python3 - "$HOOKS_FILE" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
ss = data["hooks"]["SessionStart"][0]["hooks"]
changed = False
for h in ss:
    cmd = h["command"]
    new = cmd.replace(
        'worker-service.cjs" start;',
        'worker-service.cjs" start >/dev/null 2>&1;'
    )
    if not new.startswith("{ "):
        new = "{ " + new + "; } 2>/dev/null; exit 0"
    if new != cmd:
        h["command"] = new
        changed = True
if changed:
    json.dump(data, open(path, "w"), indent=2)
    print(f"[hooks.json] parcheado {path}")
else:
    print("[hooks.json] ya parcheado")
PY

# --- Parche 2: arreglar flag --setting-sources vacío en Agent SDK bundled ---
OLD='S&&j.push("--setting-sources",S.join(","))'
NEW='S&&S.length>0&&j.push("--setting-sources",S.join(","))'
if grep -qF "$NEW" "$WORKER_FILE"; then
  echo "[worker-service.cjs] ya parcheado"
elif grep -qF "$OLD" "$WORKER_FILE"; then
  python3 - "$WORKER_FILE" "$OLD" "$NEW" <<'PY'
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path).read()
c = s.count(old)
if c != 1:
    print(f"[worker-service.cjs] {c} coincidencias para el patrón, aborto")
    sys.exit(1)
open(path, "w").write(s.replace(old, new, 1))
print(f"[worker-service.cjs] parcheado {path}")
PY
else
  echo "[worker-service.cjs] patrón --setting-sources no encontrado (SDK cambió, revisar manualmente)"
fi

# --- Parche 3: alinear puerto health-check con CLAUDE_MEM_WORKER_PORT ---
python3 - "$HOOKS_FILE" <<'PY'
import json, os, sys, re
path = sys.argv[1]

# Leer puerto configurado del worker
settings_path = os.path.expanduser("~/.claude-mem/settings.json")
try:
    port = int(json.load(open(settings_path)).get("CLAUDE_MEM_WORKER_PORT", 37777))
except Exception:
    port = 37777

data = json.load(open(path))

# Patrón original: $((37700 + $(id -u 2>/dev/null || echo 77) % 100))
OLD_PORT = r"\$\(\(37700 \+ \$\(id -u 2>/dev/null \|\| echo 77\) % 100\)\)"
# Loop de 20 iteraciones → reducido a 5; UserPromptSubmit usa loop de 10
OLD_LOOP_20 = "for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"
OLD_LOOP_10 = "for i in 1 2 3 4 5 6 7 8 9 10"
NEW_LOOP = "for i in 1 2 3 4 5"

changed = False
# Aplicar a todos los hook events que hacen health-check (SessionStart, UserPromptSubmit)
for event in ("SessionStart", "UserPromptSubmit"):
    for group in data["hooks"].get(event, []):
        for h in group.get("hooks", []):
            cmd = h["command"]
            new = re.sub(OLD_PORT, str(port), cmd)
            new = new.replace(OLD_LOOP_20, NEW_LOOP).replace(OLD_LOOP_10, NEW_LOOP)
            # Envolver UserPromptSubmit en `{ ... } 2>/dev/null; exit 0` para
            # evitar errores UI cuando el worker no responde (degradación silenciosa).
            if event == "UserPromptSubmit" and not new.startswith("{ "):
                new = "{ " + new + "; } 2>/dev/null; exit 0"
            if new != cmd:
                h["command"] = new
                changed = True

if changed:
    json.dump(data, open(path, "w"), indent=2)
    print(f"[hooks.json] port={port} + loop reducido a 5s")
else:
    print(f"[hooks.json] ya alineado (port={port}, loop=5s)")
PY
