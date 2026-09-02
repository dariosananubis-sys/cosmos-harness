#!/usr/bin/env bash
set -euo pipefail

MODEL_OVERRIDE=""
TASK=""
LOW=0
MCP_MODE="min"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --task)
      TASK="$2"
      shift 2
      ;;
    --haiku|--sonnet|--opus|--opusplan)
      MODEL_OVERRIDE="${1#--}"
      shift
      ;;
    --model)
      MODEL_OVERRIDE="$2"
      shift 2
      ;;
    --low)
      LOW=1
      shift
      ;;
    --mcp-full|--full)
      MCP_MODE="full"
      shift
      ;;
    --mcp-min)
      MCP_MODE="min"
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      if [ -z "$TASK" ] && [ "${1#-}" = "$1" ]; then
        TASK="$1"
        shift
      else
        break
      fi
      ;;
  esac
 done

if [ -z "$TASK" ] && [ -n "${CLAUDE_TASK:-}" ]; then
  TASK="$CLAUDE_TASK"
fi

if [ -z "$TASK" ] && [ -z "$MODEL_OVERRIDE" ]; then
  printf "Describe task (short): "
  read -r TASK
fi

pick_model() {
  local t
  t="$(printf "%s" "$1" | tr '[:upper:]' '[:lower:]')"

  # High-risk / complex -> Opus
  if printf "%s" "$t" | grep -Eiq "security|vulnerability|threat model|incident|root cause|data loss|compliance|audit|privacy|prod outage|postmortem|migration|rewrite|deep refactor|monorepo|multi[- ]service|distributed|concurrency|race condition|performance regression|memory leak"; then
    echo "opus"
    return
  fi

  # Planning/architecture-heavy -> Opusplan (plan with Opus, execute with Sonnet)
  if printf "%s" "$t" | grep -Eiq "architecture|design doc|system design|plan|roadmap|rfc|proposal"; then
    echo "opusplan"
    return
  fi

  # Only choose Haiku for clearly trivial edits
  if printf "%s" "$t" | grep -Eiq "typo|spelling|rename variable|rename file|format|lint|readme|docs|comment|copy change|one line|one file|css tweak|minor"; then
    echo "haiku"
    return
  fi

  # Conservative default
  echo "sonnet"
}

MODEL="$MODEL_OVERRIDE"
if [ -z "$MODEL" ]; then
  MODEL="$(pick_model "$TASK")"
fi

if [ "$LOW" -eq 1 ]; then
  export CLAUDE_CODE_MAX_OUTPUT_TOKENS="${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-1024}"
  export CLAUDE_CODE_EFFORT_LEVEL="${CLAUDE_CODE_EFFORT_LEVEL:-low}"
  export MAX_MCP_OUTPUT_TOKENS="${MAX_MCP_OUTPUT_TOKENS:-2048}"
  export CLAUDE_CODE_DISABLE_THINKING="${CLAUDE_CODE_DISABLE_THINKING:-1}"
  export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING="${CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING:-1}"
  export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="${CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS:-1}"
  export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-1}"
else
  # Balanced defaults (override by exporting before running)
  export CLAUDE_CODE_MAX_OUTPUT_TOKENS="${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-1536}"
  export CLAUDE_CODE_EFFORT_LEVEL="${CLAUDE_CODE_EFFORT_LEVEL:-low}"
  export MAX_MCP_OUTPUT_TOKENS="${MAX_MCP_OUTPUT_TOKENS:-2048}"
fi

printf "Selected model: %s\n" "$MODEL" >&2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$MCP_MODE" = "full" ]; then
  MCP_CONFIG="$SCRIPT_DIR/mcp-servers.full.json"
else
  MCP_CONFIG="$SCRIPT_DIR/mcp-servers.min.json"
fi

exec command claude --model "$MODEL" --mcp-config "$MCP_CONFIG" "$@"
