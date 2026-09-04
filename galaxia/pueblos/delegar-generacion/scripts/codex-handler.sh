#!/usr/bin/env bash
# =============================================================================
# codex-handler.sh — Smart Codex CLI delegate con control de cuota + validación
# Compatible con codex-cli 0.147.0+ (usa `codex exec -s workspace-write`; `--full-auto` ya no
# existe en el CLI, ver clap error "unexpected argument" — fix 2026-08-18)
#
# Uso: ./scripts/codex-handler.sh "tu prompt" output/file.ext [--skip-review]
#
# Diferencia con versiones anteriores:
#   - Usa `codex exec -s workspace-write` en vez de `codex --approval-mode full-auto`
#   - Codex escribe el archivo directamente (no captura stdout)
#   - El prompt debe incluir la ruta absoluta del archivo a generar
#   - El working dir se fija al workspace para que Codex encuentre el contexto
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

PROMPT="${1:-}"
OUTPUT_FILE="${2:-}"
SKIP_REVIEW="${3:-}"

# ── Validación de argumentos ──────────────────────────────────────────────────
if [[ -z "$PROMPT" || -z "$OUTPUT_FILE" ]]; then
  echo "Uso: $0 \"<prompt>\" <output_file> [--skip-review]" >&2
  exit 1
fi

# Resolver ruta absoluta del output
if [[ "$OUTPUT_FILE" != /* ]]; then
  OUTPUT_FILE="$WORKSPACE_DIR/$OUTPUT_FILE"
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

# ── Detección de errores de cuota ─────────────────────────────────────────────
is_quota_error() {
  echo "$1" | grep -qiE '429|rate.?limit|insufficient.?balance|quota.?exceeded|billing|out.?of.?credits'
}

# ── Alerta visual disruptiva ──────────────────────────────────────────────────
quota_alert() {
  printf "\n\n"
  printf "  ╔══════════════════════════════════════════════════════╗\n"
  printf "  ║  [!!!]  ALERTA: CUOTA DE CODEX AGOTADA  [!!!]       ║\n"
  printf "  ╚══════════════════════════════════════════════════════╝\n\n"
  printf "  → ENTER para reintentar, 'abort' para salir.\n\n  > "
  read -r response
  [[ "$response" == "abort" ]] && { echo "Abortado." >&2; exit 2; }
}

# ── Ejecución de Codex con reintentos ante cuota ──────────────────────────────
# codex exec -s workspace-write escribe archivos directamente (approval=never es el default de
# `exec`, no interactivo).
# El prompt debe indicar la ruta exacta del archivo a crear/reescribir.
run_codex() {
  local tmp_err
  tmp_err=$(mktemp)

  # Inyectar la ruta absoluta en el prompt para que Codex sepa dónde escribir
  local full_prompt="$PROMPT

IMPORTANTE: El archivo de salida debe escribirse en la ruta exacta: $OUTPUT_FILE
Crea o sobreescribe ese archivo con el código completo generado."

  local CODEX_TIMEOUT="${CODEX_TIMEOUT:-180}"   # s antes de sospechar cuelgue
  local codex_updated=""
  while true; do
    # Ejecutar desde el workspace para que Codex tenga contexto del proyecto.
    # Timeout portable (macOS no trae `timeout`): bg + poll + kill. Si se cuelga
    # (causa habitual: codex-cli desactualizado) -> actualizar codex y reintentar 1 vez.
    (cd "$WORKSPACE_DIR" && codex exec -s workspace-write "$full_prompt") 2> "$tmp_err" &
    local _cpid=$! _w=0 exit_code=0
    while kill -0 "$_cpid" 2>/dev/null; do
      sleep 3; _w=$((_w+3))
      if [[ $_w -ge $CODEX_TIMEOUT ]]; then
        kill -9 "$_cpid" 2>/dev/null || true; wait "$_cpid" 2>/dev/null || true
        exit_code=124; break
      fi
    done
    if [[ $exit_code -ne 124 ]]; then wait "$_cpid"; exit_code=$?; fi

    if [[ $exit_code -eq 124 ]]; then
      if [[ -z "$codex_updated" ]]; then
        echo "  ⏱ Codex tardó >${CODEX_TIMEOUT}s (posible cuelgue por codex-cli desactualizado)." >&2
        echo "  → Actualizando codex (npm i -g @openai/codex@latest) y reintentando una vez..." >&2
        npm i -g @openai/codex@latest >/dev/null 2>&1 || echo "  ⚠ no se pudo actualizar codex" >&2
        codex_updated="1"; continue
      fi
      echo "  ✗ Codex sigue colgándose tras actualizar (>${CODEX_TIMEOUT}s). Aborto." >&2
      rm -f "$tmp_err"; exit 124
    fi

    if [[ $exit_code -ne 0 ]] && is_quota_error "$(cat "$tmp_err")"; then
      cat "$tmp_err" >&2
      quota_alert; continue
    fi

    if [[ $exit_code -ne 0 ]]; then
      echo "Error Codex (exit $exit_code):" >&2; cat "$tmp_err" >&2
      rm -f "$tmp_err"; exit $exit_code
    fi

    rm -f "$tmp_err"
    break
  done
}

# ── Validación ligera post-generación (sin re-leer el archivo completo) ───────
review_output() {
  local file="$1"
  local ext="${file##*.}"
  local errors=0
  local warnings=0

  echo ""
  echo "── Revisión automática ──────────────────────────────────────"

  if [[ ! -s "$file" ]]; then
    echo "  ✗ FALLO: archivo vacío o no generado por Codex"; return 1
  fi

  local lines
  lines=$(wc -l < "$file")
  echo "  ✓ Líneas generadas: $lines"

  # Patrones prohibidos: vacio por defecto, no asume ningun sistema de diseno concreto.
  # Personaliza con CODEX_FORBIDDEN_PATTERNS="patron1,patron2,..." para tu propio proyecto.
  local forbidden=()
  if [[ -n "${CODEX_FORBIDDEN_PATTERNS:-}" ]]; then
    IFS=',' read -ra forbidden <<< "$CODEX_FORBIDDEN_PATTERNS"
  fi
  for pattern in "${forbidden[@]}"; do
    local count
    count=$(grep -c "$pattern" "$file" 2>/dev/null || true)
    if [[ $count -gt 0 ]]; then
      echo "  ⚠ AVISO: '$pattern' encontrado ($count vez/veces) — revisar"
      ((warnings++)) || true
    fi
  done

  # Checks por extensión
  if [[ "$ext" == "jsx" || "$ext" == "tsx" ]]; then
    grep -q "export default" "$file" \
      && echo "  ✓ export default presente" \
      || { echo "  ✗ Falta export default"; ((errors++)) || true; }

    # Marcadores de tu propio sistema de diseño (hook de tema, objeto de tokens, etc.):
    # CODEX_DESIGN_SYSTEM_MARKERS="useTheme|isDark|..." — vacio por defecto, se omite el check.
    if [[ -n "${CODEX_DESIGN_SYSTEM_MARKERS:-}" ]]; then
      grep -qE "$CODEX_DESIGN_SYSTEM_MARKERS" "$file" \
        && echo "  ✓ Sistema de diseño (marcadores propios) detectado" \
        || echo "  ⚠ AVISO: no se detectan los marcadores de tu sistema de diseño — verificar si aplica"
    fi
  fi

  if [[ "$ext" == "js" || "$ext" == "ts" || "$ext" == "jsx" || "$ext" == "tsx" ]]; then
    grep -q "^import\|^const\|^function\|^export" "$file" \
      && echo "  ✓ Estructura de módulo detectada" \
      || { echo "  ✗ Estructura de módulo no reconocida"; ((errors++)) || true; }
  fi

  echo ""
  echo "── Preview (head -15) ───────────────────────────────────────"
  head -15 "$file"
  echo "─────────────────────────────────────────────────────────────"

  if [[ $errors -gt 0 ]]; then
    echo ""
    echo "  ✗ $errors error(s) crítico(s) — revisar antes de usar el archivo."
    return 1
  fi

  if [[ $warnings -gt 0 ]]; then
    echo ""
    echo "  ⚠ $warnings aviso(s) — revisar manualmente."
  else
    echo ""
    echo "  ✓ Revisión superada sin problemas."
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────
echo "⟳ Delegando a Codex → $OUTPUT_FILE"
echo "  Prompt: ${PROMPT:0:120}..."
echo ""

run_codex

if [[ "$SKIP_REVIEW" != "--skip-review" ]]; then
  review_output "$OUTPUT_FILE"
fi
