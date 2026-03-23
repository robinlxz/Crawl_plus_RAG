#!/usr/bin/env bash
set -euo pipefail
[ "${VERBOSE:-1}" = "1" ] && set -x

log() { echo "[INFO] $*"; }
err() { echo "[ERROR] $*" 1>&2; }
fail() { err "$*"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EXT_DIR="${HOME}/.openclaw/extensions/byteplus-ecs-search"

PY_BIN="$ROOT_DIR/venv/bin/python"
CLI_PATH="$ROOT_DIR/src/retrieval/query_cli.py"
INDEX_PATH="$ROOT_DIR/data/byteplus.index"
META_PATH="$ROOT_DIR/data/byteplus_meta.json"

command -v "$PY_BIN" >/dev/null 2>&1 || fail "Python venv not found: $PY_BIN"
[ -s "$CLI_PATH" ] || fail "query_cli missing: $CLI_PATH"
[ -s "$INDEX_PATH" ] || fail "Index file missing: $INDEX_PATH"
[ -s "$META_PATH" ] || fail "Meta file missing: $META_PATH"

log "Creating OpenClaw extension dir: $EXT_DIR"
mkdir -p "$EXT_DIR"

log "Writing tools.json..."
cat > "$EXT_DIR/tools.json" <<JSON
{
  "name": "byteplus-ecs-search",
  "description": "Search BytePlus ECS RAG index via process tool",
  "tools": [
    {
      "name": "search_byteplus_ecs",
      "runtime": "process",
      "command": "$PY_BIN",
      "args": [
        "$CLI_PATH",
        "--query", "{{query}}",
        "--top_k", "{{top_k}}",
        "--index_path", "$INDEX_PATH",
        "--meta_path", "$META_PATH"
      ],
      "inputs": {
        "query": { "type": "string", "required": true },
        "top_k": { "type": "number", "required": false, "default": 3 }
      }
    }
  ]
}
JSON

[ -s "$EXT_DIR/tools.json" ] || fail "tools.json missing or empty"
log "Installed process search tool. You can now invoke 'search_byteplus_ecs' in OpenClaw."

