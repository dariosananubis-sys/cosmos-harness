#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-sonnet}"
if [ "$#" -gt 0 ]; then
  shift
fi

# MCP mode (min by default)
MCP_MODE="min"
if [ "${1:-}" = "--mcp-full" ] || [ "${1:-}" = "--full" ]; then
  MCP_MODE="full"
  shift
fi

# Low-cost defaults (override by exporting the vars before running)
export CLAUDE_CODE_MAX_OUTPUT_TOKENS="${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-1024}"
export CLAUDE_CODE_EFFORT_LEVEL="${CLAUDE_CODE_EFFORT_LEVEL:-low}"
export CLAUDE_CODE_DISABLE_THINKING="${CLAUDE_CODE_DISABLE_THINKING:-1}"
export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING="${CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING:-1}"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="${CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS:-1}"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$MCP_MODE" = "full" ]; then
  MCP_CONFIG="$SCRIPT_DIR/mcp-servers.full.json"
else
  MCP_CONFIG="$SCRIPT_DIR/mcp-servers.min.json"
fi

exec claude --model "$MODEL" --mcp-config "$MCP_CONFIG" "$@"
