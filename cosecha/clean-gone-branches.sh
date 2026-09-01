#!/usr/bin/env bash
# clean-gone-branches.sh — borra ramas locales cuyo upstream remoto ya no existe (merged + eliminadas en origin).
# Patrón robado de ce-clean-gone-branches (compound-engineering, 2026-06-01).
# Uso: clean-gone-branches.sh [--dry-run]   (default: dry-run; --force para borrar de verdad)
set -euo pipefail

MODE="${1:---dry-run}"
git fetch --prune origin >/dev/null 2>&1 || true

# Ramas cuyo tracking remoto está marcado "gone" por git
gone=$(git for-each-ref --format '%(refname:short) %(upstream:track)' refs/heads \
  | awk '$2 == "[gone]" {print $1}')

if [ -z "$gone" ]; then
  echo "Sin ramas huérfanas (gone). Nada que limpiar."
  exit 0
fi

current=$(git rev-parse --abbrev-ref HEAD)

echo "Ramas locales con upstream eliminado (gone):"
echo "$gone" | sed 's/^/  - /'

if [ "$MODE" = "--force" ]; then
  echo "$gone" | while read -r b; do
    [ "$b" = "$current" ] && { echo "  skip $b (rama actual)"; continue; }
    [ "$b" = "main" ] || [ "$b" = "master" ] && { echo "  skip $b (protegida)"; continue; }
    git branch -D "$b" && echo "  borrada $b"
  done
else
  echo ""
  echo "(dry-run) Para borrar: clean-gone-branches.sh --force"
fi
