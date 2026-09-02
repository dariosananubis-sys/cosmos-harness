#!/usr/bin/env bash
# Guarda un token de GitHub nuevo (validado) en el llavero de macOS y opcionalmente
# hace el push pendiente. Patrón: nunca pasar el token por argumento (quedaría en el
# historial del shell) — se teclea oculto, se valida contra la API antes de guardarlo
# en ningún sitio, y se comprueba que tiene permiso de escritura en el repo antes de
# darlo por bueno.
#
# Uso:  ./gh-token-set.sh <owner/repo>              # pide el token, valida, guarda y pushea
#       ./gh-token-set.sh <owner/repo> --no-push     # solo guarda
#
# Variables opcionales:
#   ENV_FILE   ruta a un .env donde también dejar GITHUB_TOKEN/GITHUB_USER (si no se
#              define, no se toca ningún .env).
set -euo pipefail

REPO_SLUG="${1:?Uso: gh-token-set.sh <owner/repo> [--no-push]}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

printf 'Token de GitHub (no se muestra al teclear): '
read -rs TOKEN
printf '\n'
[ -n "$TOKEN" ] || { echo "No has escrito nada."; exit 1; }

echo "-> validando el token…"
LOGIN=$(curl -sf -H "Authorization: Bearer $TOKEN" https://api.github.com/user \
        | python3 -c 'import sys,json; print(json.load(sys.stdin).get("login",""))' 2>/dev/null || true)
[ -n "$LOGIN" ] || { echo "ERROR: el token no es válido (Bad credentials)."; exit 1; }

PUSH=$(curl -sf -H "Authorization: Bearer $TOKEN" "https://api.github.com/repos/$REPO_SLUG" \
       | python3 -c 'import sys,json; print((json.load(sys.stdin).get("permissions") or {}).get("push"))' 2>/dev/null || true)
echo "   cuenta: $LOGIN | push en $REPO_SLUG: $PUSH"
if [ "$PUSH" != "True" ]; then
  echo "ERROR: ese token es válido pero NO tiene permiso de escritura en $REPO_SLUG."
  echo "       Hay que dar acceso 'Write' a $LOGIN en el repo, o usar un token de una cuenta que ya lo tenga."
  exit 1
fi

echo "-> guardando en el llavero de macOS…"
printf 'protocol=https\nhost=github.com\n\n' | git credential-osxkeychain erase 2>/dev/null || true
printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' "$LOGIN" "$TOKEN" \
  | git credential-osxkeychain store

if [ -n "${ENV_FILE:-}" ] && [ -f "$ENV_FILE" ]; then
  echo "-> actualizando $ENV_FILE…"
  python3 - "$ENV_FILE" "$TOKEN" "$LOGIN" <<'PY'
import sys, pathlib
ruta, token, login = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
lineas, visto = [], {"GITHUB_TOKEN": False, "GITHUB_USER": False}
for l in ruta.read_text(encoding="utf-8").splitlines():
    if l.startswith("GITHUB_TOKEN="):
        l, visto["GITHUB_TOKEN"] = f"GITHUB_TOKEN={token}", True
    elif l.startswith("GITHUB_USER="):
        l, visto["GITHUB_USER"] = f"GITHUB_USER={login}", True
    lineas.append(l)
if not visto["GITHUB_TOKEN"]: lineas.append(f"GITHUB_TOKEN={token}")
if not visto["GITHUB_USER"]:  lineas.append(f"GITHUB_USER={login}")
ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
PY
fi

unset TOKEN
[ "${2:-}" = "--no-push" ] && { echo "Listo (sin push, como pediste)."; exit 0; }

echo "-> pusheando…"
git -C "$RAIZ" push origin main
echo "Hecho."
