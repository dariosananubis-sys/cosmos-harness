#!/bin/bash
# Vigila que el acceso remoto al equipo siga vivo y lo reactiva si algo lo apaga.
# Lo apaga: actualizaciones de macOS, "Compartir" en Ajustes, un reset de energia.
# Instalado en /usr/local/sbin/ y lanzado cada 5 min por
# /Library/LaunchDaemons/es.example.acceso-remoto-watchdog.plist
# Fuente versionada: scripts/acceso-remoto-watchdog.sh

LOG="/var/log/acceso-remoto-watchdog.log"
TS="$(command -v tailscale || echo /opt/homebrew/bin/tailscale)"
TS_HOSTNAME="${TS_HOSTNAME:-mac-remoto}"
CAMBIOS=0

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; }

vivo() { nc -z -G 2 -w 2 127.0.0.1 "$1" >/dev/null 2>&1; }

# --- 1. SSH (puerto 22) ---
if ! vivo 22; then
  log "SSH caido -> reactivando"
  launchctl enable system/com.openssh.sshd 2>/dev/null
  launchctl load -w /System/Library/LaunchDaemons/ssh.plist 2>/dev/null
  CAMBIOS=1
fi

# --- 2. Pantalla compartida (puerto 5900) ---
if ! vivo 5900; then
  log "Screen Sharing caido -> reactivando"
  launchctl enable system/com.apple.screensharing 2>/dev/null
  launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist 2>/dev/null
  CAMBIOS=1
fi

# --- 3. Tailscale (la via de entrada desde fuera de casa) ---
if [ -x "$TS" ]; then
  ESTADO="$("$TS" status --json 2>/dev/null | /usr/bin/python3 -c \
    'import json,sys
try: print(json.load(sys.stdin).get("BackendState",""))
except Exception: print("")' 2>/dev/null)"
  if [ "$ESTADO" != "Running" ]; then
    log "Tailscale en estado '$ESTADO' -> relanzando"
    launchctl kickstart -k system/homebrew.mxcl.tailscale 2>/dev/null
    sleep 8
    # --ssh=false a proposito: con Tailscale SSH encendido, tailscaled intercepta el
    # puerto 22 y decide por ACL del tailnet, ignorando authorized_keys. Eso dejo a
    # a un usuario fuera ("tailnet policy does not permit you to SSH to this node").
    "$TS" up --ssh=false --hostname="$TS_HOSTNAME" --accept-risk=all --timeout=20s >/dev/null 2>&1
    NUEVO="$("$TS" status --json 2>/dev/null | /usr/bin/python3 -c \
      'import json,sys
try: print(json.load(sys.stdin).get("BackendState",""))
except Exception: print("")' 2>/dev/null)"
    if [ "$NUEVO" != "Running" ]; then
      log "AVISO: Tailscale sigue en '$NUEVO'. Puede necesitar login a mano."
    fi
    CAMBIOS=1
  fi
fi

# --- 4. Que el Mac no se duerma ni se quede apagado tras un corte de luz ---
DORMIR="$(pmset -g custom 2>/dev/null | awk '/^ *sleep/{print $2; exit}')"
if [ "$DORMIR" != "0" ]; then
  log "El Mac volvia a dormirse (sleep=$DORMIR) -> forzando 0"
  pmset -a sleep 0 disksleep 0 womp 1 autorestart 1 2>/dev/null
  CAMBIOS=1
fi

[ "$CAMBIOS" = "1" ] && log "--- reparacion terminada ---"

# Log acotado: nunca mas de 500 lineas
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 500 ]; then
  tail -n 200 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
exit 0
