#!/usr/bin/env bash
# =============================================================================
# codex-delegate.sh — Orquestador de dos LLM: uno planifica, Codex CLI genera.
#
# Patrón: en vez de escribir tú el código, un modelo "arquitecto" (aquí, Claude
# en modo --print) redacta el prompt ÓPTIMO y autocontenido para Codex CLI, que
# es quien realmente genera el fichero. Separa "decidir qué construir" de
# "teclear el código" y deja el prompt de Codex documentado (lo ves antes de que
# corra).
#
# Modo A (estándar):  ./codex-delegate.sh <output> "<descripción>"
# Modo B (absoluto):  ./codex-delegate.sh <output> "<descripción>" --no-review
# Con autorevisión:   ./codex-delegate.sh <output> "<descripción>" --self-review
# Sin terminal:       ./codex-delegate.sh <output> "<descripción>" --no-terminal
#
# Por defecto ejecuta inline (sin ventana). Usa --terminal para abrir una ventana
# visible en Windows (Git Bash/WSL, vía cmd.exe).
#
# Requiere: `claude` y `codex` en PATH, y codex-handler.sh al lado de este script
# (hace la llamada real a `codex exec`).
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

OUTPUT_FILE="${1:-}"
TASK_DESCRIPTION="${2:-}"
NO_REVIEW=""
SELF_REVIEW=""
# Por defecto: abrir ventana visible solo en Windows (Git Bash / WSL).
# En macOS/Linux ejecutar inline (no hay cmd.exe para spawnar terminal).
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || -n "${WSL_DISTRO_NAME:-}" ]]; then
  OPEN_TERMINAL="true"
else
  OPEN_TERMINAL=""
fi

# Parse flags (pueden venir en cualquier orden)
for arg in "${@:3}"; do
  case "$arg" in
    --no-review)    NO_REVIEW="true" ;;
    --self-review)  SELF_REVIEW="true" ;;
    --terminal)     OPEN_TERMINAL="true" ;;   # ya es default, se mantiene por compatibilidad
    --no-terminal)  OPEN_TERMINAL="" ;;       # desactivar ventana visible
  esac
done

if [[ -z "$OUTPUT_FILE" || -z "$TASK_DESCRIPTION" ]]; then
  echo "Uso: $0 <output_file> \"<descripción>\" [--no-review] [--self-review] [--no-terminal]" >&2
  exit 1
fi

EXT="${OUTPUT_FILE##*.}"

# ── Detección de proyecto (opcional) ──────────────────────────────────────────
# Si tu workspace tiene varios proyectos con reglas propias (stack, convenciones),
# añade aquí tus propios `elif` y deja las reglas de cada uno en un heredoc como
# el que se muestra comentado más abajo. Por defecto no distingue ninguno.
detect_project() {
  echo "generic"
}

PROJECT=$(detect_project "$OUTPUT_FILE")

# ── Contexto del workspace (si tienes un CLAUDE.md / AGENTS.md raíz) ──────────
WORKSPACE_CONTEXT=$(head -60 "$WORKSPACE_DIR/CLAUDE.md" 2>/dev/null || true)

# ── Contexto del proyecto concreto (si detect_project distingue alguno) ───────
PROJECT_CONTEXT=""
if [[ "$PROJECT" != "generic" ]]; then
  PROJECT_CONTEXT=$(cat "$WORKSPACE_DIR/projects/$PROJECT/CLAUDE.md" 2>/dev/null | head -120 || true)
fi

# ── Skills/herramientas disponibles en el workspace, si las hay ──────────────
SKILLS_LIST=$(ls "$WORKSPACE_DIR/.claude/skills/" 2>/dev/null | sed 's/\.md$//' | tr '\n' ', ' || true)

# ── Fase 1: el arquitecto genera el prompt óptimo para Codex ─────────────────
echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  Fase 1 · planificando el prompt para Codex...               │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

OPUS_META_PROMPT="Eres un arquitecto de software senior.
Tu tarea: redactar el prompt ÓPTIMO para Codex CLI que generará el siguiente archivo.

══════════════════════════════════════════════════
ARCHIVO DE SALIDA: $OUTPUT_FILE
EXTENSIÓN: $EXT
PROYECTO DETECTADO: $PROJECT
TAREA: $TASK_DESCRIPTION
══════════════════════════════════════════════════

CONTEXTO DEL WORKSPACE:
$WORKSPACE_CONTEXT

CONTEXTO DEL PROYECTO ($PROJECT):
$PROJECT_CONTEXT

HERRAMIENTAS/SKILLS DISPONIBLES: $SKILLS_LIST
- Codex tiene acceso completo al filesystem del workspace
- Puede leer cualquier archivo de referencia del proyecto para extraer patrones

INSTRUCCIONES PARA EL PROMPT QUE DEBES GENERAR:
El prompt debe ser AUTOCONTENIDO (Codex no tiene contexto de esta conversación).
Debe incluir:
1. Stack y proyecto concreto
2. Estructura exacta esperada (exports, props, params, tipos)
3. Qué archivos del workspace leer como referencia de patrón
4. Restricciones explícitas (qué NO hacer) para maximizar calidad sin revisión
5. Ruta exacta donde escribir el archivo de salida
6. Máximo 600 palabras — priorizar precisión sobre brevedad

Genera ÚNICAMENTE el prompt para Codex. Sin explicaciones, sin markdown extra."

CODEX_PROMPT=$(claude \
  --model opus \
  --print \
  --no-session-persistence \
  "$OPUS_META_PROMPT" 2>/dev/null)

echo "✓ Prompt generado (${#CODEX_PROMPT} chars)"
echo ""
echo "── Prompt que recibirá Codex ────────────────────────────────"
echo "$CODEX_PROMPT"
echo "─────────────────────────────────────────────────────────────"
echo ""

# Confirmación antes de ejecutar Codex
# En Modo B (--no-review) la confirmación es automática — no interrumpir flujo no-interactivo
if [[ -n "$NO_REVIEW" ]]; then
  echo "✓ Modo B — confirmación automática, ejecutando Codex..."
  confirm="S"
elif [[ ! -t 0 ]]; then
  # Sin TTY (background / --no-terminal): no hay stdin para el read → auto-sí.
  # Evita el cuelgue a 0% CPU cuando se lanza en background.
  echo "✓ Sin TTY — confirmación automática, ejecutando Codex..."
  confirm="S"
else
  read -rp "¿Ejecutar Codex con este prompt? [S/n] " confirm
  confirm="${confirm:-S}"
fi
if [[ "$confirm" != "s" && "$confirm" != "S" ]]; then
  echo "Cancelado. Para ejecutar manualmente:"
  echo "  ./codex-handler.sh \"<prompt>\" $OUTPUT_FILE"
  exit 0
fi

# ── Fase 2: Codex genera el código ───────────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
if [[ -n "$NO_REVIEW" ]]; then
echo "│  Fase 2 · Codex generando código... [MODO B — SIN REVISIÓN] │"
else
echo "│  Fase 2 · Codex generando código... [MODO A — CON REVISIÓN] │"
fi
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

HANDLER_FLAGS=""
[[ -n "$NO_REVIEW" ]] && HANDLER_FLAGS="--skip-review"

# ── Modo --terminal: abrir ventana visible en lugar de ejecutar aquí ─────────
if [[ -n "$OPEN_TERMINAL" ]]; then
  PROMPT_FILE=$(mktemp -t codex-delegate.XXXXXX)
  mv "$PROMPT_FILE" "$PROMPT_FILE.txt"
  PROMPT_FILE="$PROMPT_FILE.txt"
  printf '%s\n\nIMPORTANTE: El archivo de salida debe escribirse en la ruta exacta: %s\nCrea o sobreescribe ese archivo con el código completo generado.' \
    "$CODEX_PROMPT" "$OUTPUT_FILE" > "$PROMPT_FILE"
  echo ""
  echo "┌─────────────────────────────────────────────────────────────┐"
  echo "│  Modo TERMINAL — abriendo ventana visible para Codex        │"
  echo "└─────────────────────────────────────────────────────────────┘"
  echo "  Prompt: $PROMPT_FILE"
  echo "  Output: $OUTPUT_FILE"
  echo ""
  # Lanza nueva terminal Windows con Codex visible
  cmd.exe /c "start \"Codex — $(basename "$OUTPUT_FILE")\" bash -c \
    \"cd '$WORKSPACE_DIR' && codex exec -s workspace-write \\\"\$(cat '$PROMPT_FILE')\\\" ; \
    echo '' ; echo '✓ Codex terminado — pulsa Enter para cerrar' ; read\""
  echo "  ✓ Ventana abierta."
  exit 0
fi

"$SCRIPT_DIR/codex-handler.sh" "$CODEX_PROMPT" "$OUTPUT_FILE" $HANDLER_FLAGS

# ── Fase 3 (solo Modo A + --self-review): autorevisión de Codex ──────────────
if [[ -z "$NO_REVIEW" && -n "$SELF_REVIEW" ]]; then
  echo ""
  echo "┌─────────────────────────────────────────────────────────────┐"
  echo "│  Fase 3 · Codex autorevisando el output...                  │"
  echo "└─────────────────────────────────────────────────────────────┘"
  echo ""

  REVIEW_PROMPT="Revisa y corrige si es necesario el archivo: $OUTPUT_FILE

Comprueba:
1. Imports correctos, sin dependencias inexistentes
2. Sin variables/funciones usadas pero no definidas
3. Sintaxis correcta y archivo compilable
4. Sigue las convenciones del resto del proyecto (mira ficheros vecinos)

Si el archivo está correcto, no lo toques. Informa qué encontraste."

  (cd "$WORKSPACE_DIR" && codex exec -s workspace-write "$REVIEW_PROMPT") \
    && echo "  ✓ Autorevisión completada" \
    || echo "  ⚠ Autorevisión falló (revisar manualmente)"
fi

# ── Resumen final ─────────────────────────────────────────────────────────────
echo ""
if [[ -n "$NO_REVIEW" ]]; then
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  ✓ Modo B — Absoluto completado (sin revisión)              │"
echo "│  → $OUTPUT_FILE"
echo "└─────────────────────────────────────────────────────────────┘"
else
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  ✓ Modo A — Estándar completado                             │"
echo "│  → $OUTPUT_FILE"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""
echo "Próximos pasos:"
echo "  · Ejecuta el proyecto y comprueba el resultado"
echo "  · Si hay ⚠ warnings → re-ejecuta con --self-review"
echo "  · Correcciones manuales solo para ajustes de <5 líneas"
fi
