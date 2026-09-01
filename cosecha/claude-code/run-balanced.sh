#!/usr/bin/env bash
set -euo pipefail

MODEL="sonnet"
MCP_MODE="min"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --mcp-full|--full)
      MCP_MODE="full"
      shift
      ;;
    --mcp-min)
      MCP_MODE="min"
      shift
      ;;
    *)
      # Allow first positional model override
      if [ -z "${MODEL_OVERRIDE_SEEN:-}" ] && [ "${1#-}" = "$1" ]; then
        MODEL="$1"
        MODEL_OVERRIDE_SEEN=1
        shift
      else
        break
      fi
      ;;
  esac
 done

# Balanced defaults (override by exporting before running)
export CLAUDE_CODE_MAX_OUTPUT_TOKENS="${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-1536}"
export CLAUDE_CODE_EFFORT_LEVEL="${CLAUDE_CODE_EFFORT_LEVEL:-low}"
export MAX_MCP_OUTPUT_TOKENS="${MAX_MCP_OUTPUT_TOKENS:-2048}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$MCP_MODE" = "full" ]; then
  MCP_CONFIG="$SCRIPT_DIR/mcp-servers.full.json"
else
  MCP_CONFIG="$SCRIPT_DIR/mcp-servers.min.json"
fi

exec claude --model "$MODEL" --mcp-config "$MCP_CONFIG" "$@"
