#!/usr/bin/env bash
set -euo pipefail
[ "${VERBOSE:-1}" = "1" ] && set -x

log() { echo "[INFO] $*"; }
err() { echo "[ERROR] $*" 1>&2; }
fail() { err "$*"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

log "Project root: $ROOT_DIR"

# 1) Create venv and install deps
if [ ! -d "venv" ]; then
  log "Creating Python venv..."
  python3 -m venv venv || fail "Failed to create venv"
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2) Minimal re-crawl (10 pages), process, build index (explicit orchestration)
DATA_DIR="$ROOT_DIR/data"
INDEX_PATH="$DATA_DIR/byteplus.index"
META_PATH="$DATA_DIR/byteplus_meta.json"

log "Starting minimal crawl (MAX_PAGES_PER_SOURCE=10)..."
python3 src/crawler/byteplus_crawler.py

log "Processing raw data into blocks..."
python3 src/processor/simple_rag_processor.py

log "Building FAISS index..."
python3 src/retrieval/build_index.py

log "Index built at: $INDEX_PATH"
log "Meta saved at:  $META_PATH"

# 3) Quick verify: run query_cli with a sample query
log "Verifying retrieval with query_cli..."
python3 src/retrieval/query_cli.py --query "ESSD_FlexPL" --top_k 3 || err "query_cli verification failed"

log "Done. You can now register OpenClaw process tool pointing to:"
log "  Python: $ROOT_DIR/venv/bin/python"
log "  CLI:    $ROOT_DIR/src/retrieval/query_cli.py"
log "Default index path: $INDEX_PATH"
log "Default meta path:  $META_PATH"

