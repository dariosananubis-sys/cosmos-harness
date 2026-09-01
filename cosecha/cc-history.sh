#!/usr/bin/env bash
# cc-history.sh — historial de comandos bash que Claude Code ejecutó en las sesiones.
# Wrapper sobre eckardt/cchistory (MIT), corre on-demand vía npx (sin instalación global).
#
# Uso:
#   tools/cc-history.sh                 # historial del proyecto actual
#   tools/cc-history.sh --global        # todos los proyectos, cronológico
#   tools/cc-history.sh -g | grep rsync # auditar despliegues rsync a prod
#   tools/cc-history.sh --include-failed # incluir comandos que fallaron
#   tools/cc-history.sh -f              # follow (tail -f de comandos nuevos)
#
# Lee ~/.claude/projects/ directo. No toca la red ni exige API key.
set -euo pipefail
exec npx -y cchistory@latest "$@"
