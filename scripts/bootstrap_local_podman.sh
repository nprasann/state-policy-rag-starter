#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-}"

if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

EMBEDDING_MODEL="${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2}"
SAMPLE_POLICY_FILE="${SAMPLE_POLICY_FILE:-$ROOT_DIR/examples/sample_policy.pdf}"
SAMPLE_POLICY_NAME="${SAMPLE_POLICY_NAME:-Sample Policy}"
SAMPLE_POLICY_SECTION="${SAMPLE_POLICY_SECTION:-General}"

wait_for_url() {
  local url="$1"
  local label="$2"
  local max_attempts="${3:-60}"
  local attempt=1

  until curl --silent --fail "$url" >/dev/null; do
    if (( attempt >= max_attempts )); then
      echo "Timed out waiting for $label at $url" >&2
      exit 1
    fi

    echo "Waiting for $label ($attempt/$max_attempts)..."
    sleep 2
    attempt=$((attempt + 1))
  done
}

if command -v podman-machine >/dev/null 2>&1; then
  podman machine start >/dev/null 2>&1 || true
fi

mkdir -p qdrant_data ollama

echo "Starting local services with Podman..."
podman-compose up --build -d

wait_for_url "http://127.0.0.1:8080/health" "MCP health"
wait_for_url "http://127.0.0.1:8081/health" "RAG health"

if [[ -f "$SAMPLE_POLICY_FILE" ]]; then
  echo "Ingesting sample policy into Qdrant..."
  EMBEDDING_MODEL="$EMBEDDING_MODEL" \
  QDRANT_PORT=6333 \
  "$PYTHON_BIN" ingest/ingest.py \
    --file "$SAMPLE_POLICY_FILE" \
    --source_name "$SAMPLE_POLICY_NAME" \
    --section "$SAMPLE_POLICY_SECTION"
else
  echo "Skipping sample ingest because $SAMPLE_POLICY_FILE does not exist."
fi

wait_for_url "http://127.0.0.1:8080/ready" "MCP readiness"
wait_for_url "http://127.0.0.1:8081/ready" "RAG readiness and Ollama warmup" 120

echo "State Policy RAG starter is ready with Podman."
echo "MCP: http://127.0.0.1:8080/ready"
echo "RAG: http://127.0.0.1:8081/ready"
