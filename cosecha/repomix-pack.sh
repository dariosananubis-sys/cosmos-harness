#!/usr/bin/env bash
# repomix-pack.sh — empaqueta un repo/dir a Markdown para volcado de contexto.
# Usa la config del repo si existe (repomix.config.json): respeta .gitignore, excluye
# lo que tú marques y binarios; escaneo de secretos activo.
#
# Uso:
#   repomix-pack.sh                          # empaqueta la raíz del repo
#   repomix-pack.sh <ruta/al/subdir>         # empaqueta un subdir/repo
#   repomix-pack.sh --include "src/**/*.ts"  # override de patrón
#
# Salida: repomix-output.md (recuerda añadirlo a .gitignore). Pásaselo a un LLM como contexto.
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
exec npx -y repomix@latest "$@"
