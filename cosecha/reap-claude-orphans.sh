#!/usr/bin/env bash
# reap-claude-orphans.sh — mata procesos `claude` HUÉRFANOS (PPID=1, su sesión padre
# ya murió) y los servidores MCP (node/python) que dejaron colgados.
#
# Por qué existe: en máquinas con poca RAM, cada Claude Code arranca varios servidores
# MCP. Al cerrar/crashear una sesión sin limpiar, quedan zombis PPID=1 que acumulan RAM
# hasta agotar el swap -> thrashing -> lag -> más crashes (espiral de muerte).
#
# SEGURO POR DISEÑO: solo toca PPID=1 (padre muerto). La sesión ACTIVA tiene padre
# vivo (terminal/IDE) -> PPID != 1 -> nunca se toca. Además excluye explícitamente su
# propio claude ancestro. No pide confirmación: solo mata lo que ya está roto.
#
# Uso:
#   reap-claude-orphans.sh          barrido real
#   reap-claude-orphans.sh --dry    solo informa, no mata

set -uo pipefail
DRY=0
[ "${1:-}" = "--dry" ] && DRY=1

# --- localizar el claude ancestro de ESTE proceso, para nunca matarlo ---
self_claude=""
pid=$$
while [ "$pid" -gt 1 ]; do
  read -r ppid comm < <(ps -o ppid=,comm= -p "$pid" 2>/dev/null | awk '{print $1, $2}')
  [ -z "${ppid:-}" ] && break
  case "$comm" in *claude*) self_claude="$pid"; break;; esac
  pid="$ppid"
done

snap() { # imprime estado resumido
  printf "  claude=%s node=%s python=%s procs=%s | swap_used=%s\n" \
    "$(pgrep -x claude | wc -l | tr -d ' ')" \
    "$(pgrep -x node | wc -l | tr -d ' ')" \
    "$(pgrep -fil python 2>/dev/null | wc -l | tr -d ' ')" \
    "$(ps -A | wc -l | tr -d ' ')" \
    "$(sysctl -n vm.swapusage 2>/dev/null | sed -E 's/.*used = ([0-9.,]+M).*/\1/')"
}

orphan_claude() { # claude con PPID=1, excluyendo el propio
  ps -Ao pid,ppid,comm | awk -v me="${self_claude:-0}" \
    '$2==1 && $3=="claude" && $1!=me {print $1}'
}
orphan_mcp() { # node/python con PPID=1 (MCP dejados colgando)
  ps -Ao pid,ppid,comm | awk '$2==1 && ($3 ~ /node/ || $3 ~ /[Pp]ython/) {print $1}'
}

echo "== reap-claude-orphans =="
[ -n "$self_claude" ] && echo "  (mi claude activo = $self_claude, protegido)"
echo "ANTES:"; snap

ORPH="$(orphan_claude)"
if [ -z "$ORPH" ]; then
  echo "  sin claude huérfanos."
else
  echo "  huérfanos: $(echo $ORPH | tr '\n' ' ')"
  if [ "$DRY" = "1" ]; then
    echo "  [--dry] no se mata nada."
  else
    for p in $ORPH; do kill -TERM "$p" 2>/dev/null; done
    perl -e 'select(undef,undef,undef,3)' 2>/dev/null || sleep 3
    for p in $ORPH; do kill -0 "$p" 2>/dev/null && kill -9 "$p" 2>/dev/null; done
    # reaper 2º intento: en swap-thrashing algunos quedan en D-state y no mueren al 1er KILL
    perl -e 'select(undef,undef,undef,2)' 2>/dev/null || sleep 2
    for p in $ORPH; do kill -0 "$p" 2>/dev/null && kill -9 "$p" 2>/dev/null; done
  fi
fi

# barrer MCP huérfanos que quedaron tras morir sus claude padre
if [ "$DRY" = "0" ]; then
  MCP="$(orphan_mcp)"
  if [ -n "$MCP" ]; then
    echo "  MCP huérfanos: $(echo $MCP | wc -w | tr -d ' ')"
    for p in $MCP; do kill -TERM "$p" 2>/dev/null; done
    perl -e 'select(undef,undef,undef,2)' 2>/dev/null || sleep 2
    for p in $MCP; do kill -0 "$p" 2>/dev/null && kill -9 "$p" 2>/dev/null; done
  fi
fi

echo "DESPUÉS:"; snap
echo "== fin =="
