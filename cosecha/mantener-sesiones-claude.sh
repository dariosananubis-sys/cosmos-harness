#!/usr/bin/env bash
# mantener-sesiones.sh — que LAS DOS cuentas de Claude sigan iniciadas siempre.
#
# Orden de Darío (2026-08-17): *"que siempre estemos logueados en ambas y yo elijo con el
# botón; no salir de una y dejarla apartada"*.
#
# El problema que resuelve: cada cuenta vive en su `CLAUDE_CONFIG_DIR` aislado con su propio
# item de llavero, así que estar en las dos a la vez YA funciona. Lo que no funciona solo es
# el tiempo: el refresh token dura ~9 días, y una cuenta que nadie usa en ese plazo se queda
# sin sesión y pide `/login` a mano. Es lo que le pasa a una cuenta apartada tiempo,
# muerta el 2026-08-17: "OAuth session expired and could not be refreshed").
#
# La cura es usarla de vez en cuando: una llamada mínima con su config dir hace que el CLI
# renueve y persista su token él mismo — que es la forma segura, porque el refresh token rota
# y escribirlo a mano desde fuera dejaría la cuenta sin sesión (por eso `quota-oficial.py`
# tampoco lo renueva).
#
# `auth status` no renueva el OAuth (solo inspecciona estado), así que mantener una cuenta
# inactiva exige una inferencia mínima. El LaunchAgent revisa cada 2 días, pero un marcador
# privado limita la inferencia de cada cuenta a una vez cada 4 días. La llamada usa Haiku,
# esfuerzo bajo, system prompt mínimo, cero herramientas, safe-mode y cero persistencia.
#
# Uso:
#   ./tools/mantener-sesiones.sh            # toca todas las cuentas
#   ./tools/mantener-sesiones.sh --dry-run  # dice a cuáles tocaría, sin llamar
#
# Instalado como LaunchAgent `com.example.mantener-sesiones` por tools/mantener-sesiones-instalar.sh.
set -uo pipefail   # sin -e a propósito: si una cuenta falla, se sigue con las demás

STORE="$HOME/.secrets/claude-accounts"
SESIONES="$STORE/sessions"
LOG="$HOME/.claude/logs/mantener-sesiones.log"
CLAUDE_BIN="$HOME/.local/bin/claude"
CLEAN_CWD="$STORE/keepalive-cwd"
ENTORNO_LIMPIO=(
  "HOME=$HOME"
  "PATH=$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  "USER=${USER:-$(id -un)}"
  "LOGNAME=${LOGNAME:-${USER:-$(id -un)}}"
)
[ -n "${TMPDIR:-}" ] && ENTORNO_LIMPIO+=("TMPDIR=$TMPDIR")
[ -n "${LANG:-}" ] && ENTORNO_LIMPIO+=("LANG=$LANG")
[ -n "${LC_ALL:-}" ] && ENTORNO_LIMPIO+=("LC_ALL=$LC_ALL")
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1
MIN_INTERVALO_S=345600

mkdir -p "$(dirname "$LOG")"
apunta() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" | tee -a "$LOG"; }
UID_ACTUAL="$(id -u)"
dir_privado() {
  [ -d "$1" ] && [ ! -L "$1" ] && [ "$(stat -f '%u:%Lp' "$1" 2>/dev/null)" = "$UID_ACTUAL:700" ]
}
fichero_privado() {
  [ -f "$1" ] && [ ! -L "$1" ] && [ "$(stat -f '%u:%Lp:%l' "$1" 2>/dev/null)" = "$UID_ACTUAL:600:1" ]
}

[ -L "$CLEAN_CWD" ] && { apunta "directorio limpio inseguro: no actuo"; exit 1; }
if [ -e "$CLEAN_CWD" ] && [ ! -d "$CLEAN_CWD" ]; then
  apunta "directorio limpio inseguro: no actuo"
  exit 1
fi
dir_privado "$STORE" || { apunta "almacen ausente o inseguro: no actuo"; exit 1; }
dir_privado "$SESIONES" || { apunta "sesiones ausentes o inseguras: no actuo"; exit 1; }
mkdir -p "$CLEAN_CWD"
chmod 700 "$CLEAN_CWD"
dir_privado "$CLEAN_CWD" || {
  apunta "directorio limpio ausente o inseguro: no actuo"
  exit 1
}
[ -x "$CLAUDE_BIN" ] && [ ! -L "$CLAUDE_BIN" ] || {
  # El enlace versionado de Claude es deliberado y estable; se valida su destino físico.
  [ -x "$CLAUDE_BIN" ] && [ -f "$(readlink "$CLAUDE_BIN" 2>/dev/null)" ] || {
    apunta "binario Claude ausente o inseguro: no actuo"
    exit 1
  }
}

fallos=0
for alias_cuenta in ${MANTENER_SESIONES_ALIASES:-cuenta-a cuenta-b}; do
  dir="$SESIONES/$alias_cuenta"
  ficha="$STORE/$alias_cuenta.json"
  marcador="$STORE/$alias_cuenta.keepalive"
  config_cuenta="$dir/.claude.json"
  credencial_cuenta="$dir/.credentials.json"
  # No se sigue ningún symlink: un alias cruzado podría renovar la cuenta equivocada.
  layout_inseguro=0
  dir_privado "$dir" || layout_inseguro=1
  fichero_privado "$ficha" || layout_inseguro=1
  fichero_privado "$config_cuenta" || layout_inseguro=1
  if [ -e "$marcador" ] || [ -L "$marcador" ]; then
    fichero_privado "$marcador" || layout_inseguro=1
  fi
  if [ -e "$credencial_cuenta" ] || [ -L "$credencial_cuenta" ]; then
    fichero_privado "$credencial_cuenta" || layout_inseguro=1
  fi
  if [ "$layout_inseguro" -ne 0 ]; then
    apunta "$alias_cuenta: layout ausente o inseguro; no lo toco"
    fallos=$((fallos + 1))
    continue
  fi

  # DOS directorios con la MISMA cuenta = dos sitios rotando el mismo refresh token, que es
  # exactamente como se revocó la sesión el 2026-07-30. Pasa cuando un `/login` se hace desde
  # la ventana equivocada y sobrescribe la credencial del otro alias. Aquí se toca solo el
  # primero y se avisa: tocar los dos sería provocar el incidente cada dos días.
  uuid="$(/usr/bin/python3 -c "
import json,sys
try:
    print((json.load(open(sys.argv[1]+'/.claude.json')).get('oauthAccount') or {}).get('accountUuid') or '')
except Exception:
    print('')
" "$dir" 2>/dev/null)"
  if [ -n "$uuid" ] && printf '%s\n' "${vistos:-}" | grep -qx "$uuid"; then
    apunta "$alias_cuenta: MISMA cuenta que otro alias ya tocado -> lo salto (dos sitios rotando"
    apunta "  el mismo refresh token revocan la sesion). Arreglo: haz /login aqui con SU cuenta:"
    apunta "  CLAUDE_CONFIG_DIR=\"$dir\" claude   ...y dentro:  /login"
    fallos=$((fallos + 1))
    continue
  fi
  [ -n "$uuid" ] && vistos="${vistos:-}
$uuid"

  ahora="$(date +%s)"
  ultima=0
  [ -f "$marcador" ] && ultima="$(stat -f '%m' "$marcador" 2>/dev/null || printf '0')"
  case "$ultima" in (*[!0-9]*|'') ultima=0 ;; esac
  if [ $((ahora - ultima)) -lt "$MIN_INTERVALO_S" ]; then
    apunta "$alias_cuenta: sesion ya mantenida hace menos de 4 dias; cero inferencia"
    continue
  fi

  if [ "$DRY" = "1" ]; then
    apunta "[dry-run] renovaria $alias_cuenta con la llamada minima"
    continue
  fi

  # Esta es la única inferencia del mantenimiento. No carga proyecto, skills, hooks, MCP,
  # herramientas ni sesión; el system prompt sustituye al grande por una frase estable.
  if (cd "$CLEAN_CWD" && /usr/bin/env -i "${ENTORNO_LIMPIO[@]}" \
      CLAUDE_CONFIG_DIR="$dir" "$CLAUDE_BIN" -p "ok" \
      --model claude-haiku-4-5 --effort low --max-turns 1 \
      --safe-mode --disable-slash-commands --tools "" \
      --system-prompt "Responde solo ok." --no-session-persistence \
      --prompt-suggestions false >/dev/null 2>&1); then
    temporal="$(mktemp "$STORE/.${alias_cuenta}.keepalive.XXXXXX")"
    printf '%s\n' "$ahora" > "$temporal"
    chmod 600 "$temporal"
    mv -f "$temporal" "$marcador"
    apunta "$alias_cuenta: sesion viva; proxima inferencia no antes de 4 dias"
  else
    fallos=$((fallos + 1))
    apunta "$alias_cuenta: SIN SESION -> hace falta /login a mano:"
    apunta "  CLAUDE_CONFIG_DIR=\"$dir\" claude   ...y dentro:  /login"
  fi
done

exit $((fallos > 0 ? 1 : 0))
