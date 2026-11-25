#!/usr/bin/env bash
# `make check-model`: is the local agent model ready for Claude Code?
# Exits non-zero with a plain explanation if not. Run this before `claude`.
set -uo pipefail

MODEL="${MODEL:-bikeshare-coder}"
HOST="${OLLAMA_HOST:-http://localhost:11434}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "FAIL: ollama is not installed. See https://ollama.com/download" >&2; exit 1
fi
if ! curl -fsS "$HOST/api/tags" >/dev/null 2>&1; then
  echo "FAIL: no Ollama server at $HOST. Start it with: ollama serve" >&2; exit 1
fi
if ! ollama show "$MODEL" >/dev/null 2>&1; then
  echo "FAIL: model '$MODEL' not built. Run: make model" >&2; exit 1
fi

ctx=$(ollama show "$MODEL" 2>/dev/null | awk '/num_ctx/ {print $2}' | head -1)
if [ -z "$ctx" ] || [ "$ctx" -lt 65536 ]; then
  echo "FAIL: '$MODEL' has num_ctx=${ctx:-unset}; need >= 65536. Rebuild with: make model" >&2; exit 1
fi
if ! ollama show "$MODEL" 2>/dev/null | grep -qi "tools"; then
  echo "WARN: '$MODEL' does not advertise tool support; Claude Code needs it." >&2
fi

# One real request through the Anthropic-compatible endpoint, with a tool,
# so a broken install fails here and not twenty minutes into Step 2.
if ! resp=$(curl -fsS "$HOST/v1/messages" \
  -H "content-type: application/json" -H "x-api-key: ollama" -H "anthropic-version: 2023-06-01" \
  -d "$(python - "$MODEL" <<'PY'
import json
import sys
print(json.dumps({
    "model": sys.argv[1], "max_tokens": 2048,
    "thinking": {"type": "disabled"},
    "tools": [{"name": "ping", "description": "Reply tool", "input_schema": {"type": "object", "properties": {}}}],
    "tool_choice": {"type": "tool", "name": "ping"},
    "messages": [{"role": "user", "content": "Call the ping tool with an empty object."}],
}))
PY
)"); then
  echo "FAIL: local model request failed" >&2
  exit 1
fi
if ! python -c 'import json, sys; blocks = json.load(sys.stdin).get("content", []); sys.exit(0 if any(b.get("type") == "tool_use" and b.get("name") == "ping" for b in blocks) else 1)' <<< "$resp"; then
  echo "FAIL: the local model did not call the ping tool" >&2
  exit 1
fi

echo "OK model: $MODEL at $HOST, num_ctx=$ctx, tool call works."
